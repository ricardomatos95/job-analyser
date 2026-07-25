from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class JobInput(BaseModel):
    source_type: Literal["url", "text"]
    content: str = Field(description="Job posting URL or raw job description text")


class JobRequirement(BaseModel):
    category: Literal["technical", "domain", "delivery", "leadership", "language", "other"]
    requirement: str
    importance: Literal["must_have", "nice_to_have", "unknown"] = "unknown"


class JobRequirements(BaseModel):
    job_title: str
    company: str | None = None
    location: str | None = None
    seniority: str | None = None
    requirements: list[JobRequirement]
    responsibilities: list[str]
    keywords: list[str]


class CandidateProfile(BaseModel):
    name: str
    headline: str
    summary: str
    strengths: list[str]
    experience_highlights: list[str]
    target_roles: list[str]
    preferred_locations: list[str]
    skill_gaps: list[str]


class MatchItem(BaseModel):
    requirement: str
    evidence: str
    match_strength: Literal["strong", "partial", "weak", "missing"]


class MatchAnalysis(BaseModel):
    overall_fit_score: int = Field(ge=0, le=100)
    matches: list[MatchItem]
    strongest_selling_points: list[str]


class GapAnalysis(BaseModel):
    critical_gaps: list[str]
    manageable_gaps: list[str]
    mitigation_strategy: list[str]


class GeneratedAssets(BaseModel):
    cv_bullets: list[str]
    recruiter_message: str
    interview_prep_questions: list[str]
    interview_talking_points: list[str]


class ApprovalDecision(BaseModel):
    approved: bool
    reviewer_notes: str | None = None
    rectify: bool = False
    rectify_target: str | None = None


class ChatIntent(BaseModel):
    action: Literal["analyze_job", "followup", "chitchat"]
    job_text: str | None = None
    job_url: str | None = None


class ApplicationPack(BaseModel):
    requirements: JobRequirements
    match_analysis: MatchAnalysis
    gap_analysis: GapAnalysis
    generated_assets: GeneratedAssets
    approved: bool = False
    reviewer_notes: str | None = None
