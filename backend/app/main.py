from __future__ import annotations

from csv import DictReader
from datetime import datetime, timezone
from io import StringIO
from statistics import mean

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .ai_service import AIService
from .models import LeadResult, LeadScoreBreakdown, ProcessResponse, RefineRequest, RefineResponse, Summary
from .reporting import top_leads_markdown
from .scoring import choose_tier, pick_offer_angle, score_row, summarize_state_tiers, template_outreach
from .settings import settings

app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "env": settings.app_env,
        "ai_enabled": ai_service.enabled,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/refine-outreach", response_model=RefineResponse)
def refine_outreach(payload: RefineRequest) -> RefineResponse:
    if not ai_service.enabled:
        raise HTTPException(status_code=400, detail="AI service is not enabled on backend.")

    if not payload.feedback.strip():
        raise HTTPException(status_code=400, detail="Feedback is required.")

    result = ai_service.refine_outreach(
        language=payload.language,
        tone=payload.tone,
        brand_name=payload.brand_name,
        positioning=payload.positioning,
        company_name=payload.company_name,
        city=payload.city,
        state=payload.state,
        services=payload.services,
        description=payload.description,
        current_subject=payload.current_subject,
        current_message=payload.current_message,
        feedback=payload.feedback,
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to refine outreach draft.")

    subject, message = result
    return RefineResponse(subject=subject, message=message)


@app.post("/api/process", response_model=ProcessResponse)
async def process_leads(
    file: UploadFile = File(...),
    target_states: str = Form("AZ,CA,TX,FL,NY"),
    brand_name: str = Form("Sunny Home"),
    positioning: str = Form("Mid-to-high-end furniture and lighting for premium projects."),
    tone: str = Form("confident, practical, consultative"),
    language: str = Form("EN"),
    use_ai: bool = Form(False),
    ai_limit: int = Form(10),
) -> ProcessResponse:
    normalized_language = "CN" if str(language).strip().upper() == "CN" else "EN"

    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        decoded = content.decode("utf-8-sig")
        reader = DictReader(StringIO(decoded))
        rows = list(reader)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no data rows.")

    normalized_states = {s.strip().upper() for s in target_states.split(",") if s.strip()}

    scored_rows: list[dict] = []
    for row in rows:
        breakdown, reasons, text = score_row(row, normalized_states, normalized_language)
        tier = choose_tier(breakdown.total)
        reason = ("；" if normalized_language == "CN" else "; ").join(reasons) if reasons else ("整体匹配度一般" if normalized_language == "CN" else "General fit")

        company = row.get("company_name", "Unknown")
        city = row.get("city", "")
        state = row.get("state", "")

        angle = pick_offer_angle(text, normalized_language)
        subject, message = template_outreach(company, city, angle, brand_name, normalized_language)

        scored_rows.append(
            {
                "company_name": company,
                "city": city,
                "state": state,
                "website": row.get("website", ""),
                "source": row.get("source", ""),
                "services": row.get("services", ""),
                "description": row.get("description", ""),
                "score": breakdown.total,
                "tier": tier,
                "reason": reason,
                "outreach_subject": subject,
                "outreach_message": message,
                "breakdown": breakdown,
            }
        )

    scored_rows.sort(key=lambda item: item["score"], reverse=True)

    ai_enabled = bool(use_ai and ai_service.enabled)
    if ai_enabled:
        for row in scored_rows[: max(0, ai_limit)]:
            ai_output = ai_service.generate_outreach(
                brand_name=brand_name,
                positioning=positioning,
                company_name=row["company_name"],
                city=row["city"],
                state=row["state"],
                services=row["services"],
                description=row["description"],
                tone=tone,
                language=normalized_language,
            )
            if ai_output:
                row["outreach_subject"], row["outreach_message"] = ai_output

    lead_results: list[LeadResult] = []
    for row in scored_rows:
        breakdown = row["breakdown"]
        lead_results.append(
            LeadResult(
                company_name=row["company_name"],
                city=row["city"],
                state=row["state"],
                website=row["website"],
                source=row["source"],
                services=row["services"],
                description=row["description"],
                score=row["score"],
                tier=row["tier"],
                reason=row["reason"],
                outreach_subject=row["outreach_subject"],
                outreach_message=row["outreach_message"],
                breakdown=LeadScoreBreakdown(
                    industry_fit=breakdown.industry_fit,
                    product_match=breakdown.product_match,
                    digital_signal=breakdown.digital_signal,
                    scale_signal=breakdown.scale_signal,
                    intent_signal=breakdown.intent_signal,
                    penalties=breakdown.penalties,
                    total=breakdown.total,
                ),
            )
        )

    tier_a = sum(1 for item in scored_rows if item["tier"] == "A")
    tier_b = sum(1 for item in scored_rows if item["tier"] == "B")
    tier_c = sum(1 for item in scored_rows if item["tier"] == "C")

    summary = Summary(
        total_leads=len(scored_rows),
        average_score=round(mean(item["score"] for item in scored_rows), 1),
        tier_a=tier_a,
        tier_b=tier_b,
        tier_c=tier_c,
        top_states=summarize_state_tiers([item["state"] for item in scored_rows if item["state"]]),
    )

    report_md = top_leads_markdown([lead.model_dump() for lead in lead_results], top_n=10, language=normalized_language)

    return ProcessResponse(
        brand_name=brand_name,
        language=normalized_language,
        use_ai=use_ai,
        ai_enabled=ai_enabled,
        leads=lead_results,
        summary=summary,
        top_leads_markdown=report_md,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
