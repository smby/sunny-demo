from pydantic import BaseModel, Field
from typing import List


class LeadScoreBreakdown(BaseModel):
    industry_fit: int
    product_match: int
    digital_signal: int
    scale_signal: int
    intent_signal: int
    penalties: int
    total: int


class LeadResult(BaseModel):
    company_name: str
    city: str = ""
    state: str = ""
    website: str = ""
    source: str = ""
    services: str = ""
    description: str = ""
    score: int
    tier: str
    reason: str
    outreach_subject: str
    outreach_message: str
    breakdown: LeadScoreBreakdown


class Summary(BaseModel):
    total_leads: int
    average_score: float
    tier_a: int
    tier_b: int
    tier_c: int
    top_states: List[dict[str, int]]


class ProcessResponse(BaseModel):
    brand_name: str
    language: str
    use_ai: bool
    ai_enabled: bool
    leads: List[LeadResult]
    summary: Summary
    top_leads_markdown: str
    generated_at: str = Field(description="ISO datetime")


class RefineRequest(BaseModel):
    language: str = "EN"
    tone: str
    brand_name: str
    positioning: str
    company_name: str
    city: str = ""
    state: str = ""
    services: str = ""
    description: str = ""
    current_subject: str
    current_message: str
    feedback: str


class RefineResponse(BaseModel):
    subject: str
    message: str
