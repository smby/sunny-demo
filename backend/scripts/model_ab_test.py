#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.scoring import pick_offer_angle, score_row  # noqa: E402


@dataclass
class Lead:
    company_name: str
    city: str
    state: str
    services: str
    description: str
    score: int
    reason: str


def build_prompt(*, language: str, brand_name: str, positioning: str, tone: str, lead: Lead) -> str:
    target_language = "Simplified Chinese" if language == "CN" else "English"
    return f"""
You are writing short B2B outreach for a furniture/lighting supplier.
Return strict JSON with keys: subject, body.

Brand:
- name: {brand_name}
- positioning: {positioning}

Prospect:
- company: {lead.company_name}
- city/state: {lead.city}, {lead.state}
- services: {lead.services}
- description: {lead.description}

Constraints:
- output language: {target_language}
- tone: {tone}
- keep subject under 70 chars
- keep email body under 120 words
- include one concrete value proposition
- include one clear CTA for a quick reply
- no hype, no emojis
""".strip()


def parse_json_response(text: str) -> tuple[str, str]:
    text = (text or "").strip()
    if not text:
        return "", ""

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    if text.startswith("{"):
        try:
            obj = json.loads(text)
            return str(obj.get("subject", "")).strip(), str(obj.get("body", "")).strip()
        except Exception:
            pass

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) >= 2:
        return lines[0], "\n".join(lines[1:])
    return "", ""


def read_top_leads(csv_path: Path, language: str, target_states: set[str], top_n: int) -> list[Lead]:
    leads: list[Lead] = []
    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            breakdown, reasons, text = score_row(row, target_states, language)
            reason = ("；" if language == "CN" else "; ").join(reasons) if reasons else ("整体匹配度一般" if language == "CN" else "General fit")
            leads.append(
                Lead(
                    company_name=row.get("company_name", "Unknown"),
                    city=row.get("city", ""),
                    state=row.get("state", ""),
                    services=row.get("services", ""),
                    description=row.get("description", ""),
                    score=breakdown.total,
                    reason=reason,
                )
            )
    leads.sort(key=lambda x: x.score, reverse=True)
    return leads[:top_n]


def run_model_test(
    client: OpenAI,
    model: str,
    leads: list[Lead],
    *,
    language: str,
    brand_name: str,
    positioning: str,
    tone: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    latencies: list[float] = []
    subject_lens: list[int] = []
    body_lens: list[int] = []
    success_count = 0

    for lead in leads:
        prompt = build_prompt(
            language=language,
            brand_name=brand_name,
            positioning=positioning,
            tone=tone,
            lead=lead,
        )
        start = time.perf_counter()
        error = ""
        subject = ""
        body = ""
        try:
            resp = client.responses.create(model=model, input=prompt, temperature=0.3)
            text = (resp.output_text or "").strip()
            subject, body = parse_json_response(text)
            if subject and body:
                success_count += 1
        except Exception as exc:
            error = str(exc)

        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
        subject_lens.append(len(subject))
        body_lens.append(len(body))

        rows.append(
            {
                "model": model,
                "company_name": lead.company_name,
                "lead_score": lead.score,
                "lead_reason": lead.reason,
                "latency_ms": round(latency_ms, 1),
                "subject": subject,
                "body": body,
                "subject_len": len(subject),
                "body_len": len(body),
                "error": error,
            }
        )

    summary = {
        "model": model,
        "requests": len(leads),
        "success": success_count,
        "success_rate": round((success_count / len(leads)) * 100, 1) if leads else 0.0,
        "avg_latency_ms": round(statistics.mean(latencies), 1) if latencies else 0.0,
        "p95_latency_ms": round(sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)], 1) if latencies else 0.0,
        "avg_subject_len": round(statistics.mean(subject_lens), 1) if subject_lens else 0.0,
        "avg_body_len": round(statistics.mean(body_lens), 1) if body_lens else 0.0,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summaries: list[dict[str, Any]], samples: list[dict[str, Any]], language: str) -> None:
    cn = language == "CN"
    lines = []
    lines.append("# 模型 A/B 测试报告" if cn else "# Model A/B Test Report")
    lines.append("")
    lines.append(f"- {'语言' if cn else 'Language'}: {language}")
    lines.append("")
    lines.append("## 概览" if cn else "## Summary")
    lines.append("")
    lines.append("| Model | Requests | Success | Success Rate | Avg Latency (ms) | P95 Latency (ms) | Avg Subject Len | Avg Body Len |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in summaries:
        lines.append(
            f"| {s['model']} | {s['requests']} | {s['success']} | {s['success_rate']}% | {s['avg_latency_ms']} | {s['p95_latency_ms']} | {s['avg_subject_len']} | {s['avg_body_len']} |"
        )

    lines.append("")
    lines.append("## 示例输出" if cn else "## Sample Outputs")
    lines.append("")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in samples:
        grouped.setdefault(r["model"], []).append(r)

    for model, rows in grouped.items():
        lines.append(f"### {model}")
        lines.append("")
        for row in rows[:2]:
            lines.append(f"- **{row['company_name']}** ({row['latency_ms']} ms)")
            lines.append(f"  - {'标题' if cn else 'Subject'}: {row['subject'] or '[empty]'}")
            lines.append(f"  - {'正文' if cn else 'Body'}: {row['body'][:180].replace(chr(10), ' ')}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B test OpenAI models for Sunny Demo outreach generation")
    parser.add_argument("--models", default="gpt-4o-mini,gpt-4.1-mini,gpt-4o", help="Comma-separated model list")
    parser.add_argument("--language", choices=["CN", "EN"], default="CN")
    parser.add_argument("--top-n", type=int, default=8)
    parser.add_argument("--input", default="../sample-data/sample_leads.csv")
    parser.add_argument("--target-states", default="AZ,CA,TX,FL,NY")
    parser.add_argument("--brand-name", default="Sunny Home")
    parser.add_argument("--positioning", default="面向住宅、软装与精品酒店场景的中高端家具与灯具供应方案。")
    parser.add_argument("--tone", default="专业、务实、可信")
    parser.add_argument("--output-dir", default="abtest_output")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    load_dotenv(base_dir / ".env")

    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENAI_API_KEY missing in backend/.env")

    input_csv = (base_dir / args.input).resolve()
    output_dir = (base_dir / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    target_states = {s.strip().upper() for s in args.target_states.split(",") if s.strip()}
    leads = read_top_leads(input_csv, args.language, target_states, args.top_n)

    if not leads:
        raise SystemExit("No leads loaded from input CSV")

    client = OpenAI(api_key=key)
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for model in models:
        rows, summary = run_model_test(
            client,
            model,
            leads,
            language=args.language,
            brand_name=args.brand_name,
            positioning=args.positioning,
            tone=args.tone,
        )
        all_rows.extend(rows)
        summaries.append(summary)

    summary_csv = output_dir / "model_ab_summary.csv"
    details_csv = output_dir / "model_ab_details.csv"
    report_md = output_dir / "model_ab_report.md"

    write_csv(summary_csv, summaries)
    write_csv(details_csv, all_rows)
    write_markdown(report_md, summaries, all_rows, args.language)

    print("A/B test complete")
    print(f"- Summary: {summary_csv}")
    print(f"- Details: {details_csv}")
    print(f"- Report: {report_md}")


if __name__ == "__main__":
    main()
