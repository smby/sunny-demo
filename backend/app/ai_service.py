from __future__ import annotations

import json
from typing import Optional

from .settings import settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class AIService:
    def __init__(self) -> None:
        self.enabled = bool(settings.openai_api_key and OpenAI)
        self.client = OpenAI(api_key=settings.openai_api_key) if self.enabled else None

    @staticmethod
    def _clean_json_text(text: str) -> str:
        cleaned = (text or "").strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        return cleaned

    def _call_model(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=prompt,
                temperature=0.2,
            )
            return (response.output_text or "").strip()
        except Exception as exc:
            # Some fast models reject temperature; retry without it.
            if "temperature" in str(exc).lower():
                response = self.client.responses.create(
                    model=settings.openai_model,
                    input=prompt,
                )
                return (response.output_text or "").strip()
            raise

    def generate_outreach(
        self,
        *,
        brand_name: str,
        positioning: str,
        company_name: str,
        city: str,
        state: str,
        services: str,
        description: str,
        tone: str,
        language: str,
    ) -> Optional[tuple[str, str]]:
        if not self.enabled:
            return None

        target_language = "Simplified Chinese" if language.upper() == "CN" else "English"

        prompt = f"""
You are writing short B2B outreach for a furniture/lighting supplier.
Return STRICT JSON only with keys: subject, body.

Brand:
- name: {brand_name}
- positioning: {positioning}

Prospect:
- company: {company_name}
- city/state: {city}, {state}
- services: {services}
- description: {description}

Constraints:
- output language: {target_language}
- tone: {tone}
- keep subject under 70 chars
- keep email body under 120 words
- include one concrete value proposition
- include one clear CTA for a quick reply
- no hype, no emojis
""".strip()

        try:
            text = self._call_model(prompt)
            if not text:
                return None

            # Accept either strict JSON or simple fallback format.
            cleaned = self._clean_json_text(text)
            if cleaned.startswith("{"):
                payload = json.loads(cleaned)
                subject = str(payload.get("subject", "")).strip()
                body = str(payload.get("body", "")).strip()
                if subject and body:
                    return subject, body

            lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
            if len(lines) >= 2:
                return lines[0][:70], "\n".join(lines[1:])
            return None
        except Exception:
            return None

    def refine_outreach(
        self,
        *,
        language: str,
        tone: str,
        brand_name: str,
        positioning: str,
        company_name: str,
        city: str,
        state: str,
        services: str,
        description: str,
        current_subject: str,
        current_message: str,
        feedback: str,
    ) -> Optional[tuple[str, str]]:
        if not self.enabled:
            return None

        target_language = "Simplified Chinese" if language.upper() == "CN" else "English"
        prompt = f"""
You are refining B2B outreach for a furniture/lighting supplier.
Return STRICT JSON only with keys: subject, body.

Language: {target_language}
Tone: {tone}

Brand:
- name: {brand_name}
- positioning: {positioning}

Prospect:
- company: {company_name}
- city/state: {city}, {state}
- services: {services}
- description: {description}

Current draft:
- subject: {current_subject}
- body: {current_message}

Feedback to apply:
{feedback}

Constraints:
- keep subject under 70 chars
- keep body under 120 words
- preserve concrete value proposition
- include one clear CTA
- no markdown fences, no explanation text
""".strip()

        try:
            cleaned = self._clean_json_text(self._call_model(prompt))
            if not cleaned:
                return None
            if cleaned.startswith("{"):
                payload = json.loads(cleaned)
                subject = str(payload.get("subject", "")).strip()
                body = str(payload.get("body", "")).strip()
                if subject and body:
                    return subject, body
            return None
        except Exception:
            return None
