import pytest
from app_agent.chat import classify_intent, format_history, summarize_pack
from app_agent.models import (
    ApplicationPack,
    GapAnalysis,
    GeneratedAssets,
    JobRequirement,
    JobRequirements,
    MatchAnalysis,
    MatchItem,
)


def _sample_pack() -> ApplicationPack:
    return ApplicationPack(
        requirements=JobRequirements(
            job_title="Forward-Deployed Engineer",
            requirements=[
                JobRequirement(category="technical", requirement="Kubernetes", importance="must_have")
            ],
            responsibilities=["Own delivery"],
            keywords=["GenAI"],
        ),
        match_analysis=MatchAnalysis(
            overall_fit_score=55,
            matches=[
                MatchItem(requirement="Kubernetes", evidence="None found", match_strength="missing")
            ],
            strongest_selling_points=["Enterprise stakeholder management", "GenAI delivery"],
        ),
        gap_analysis=GapAnalysis(
            critical_gaps=["No Kubernetes experience"],
            manageable_gaps=["Limited Go experience"],
            mitigation_strategy=["Highlight transferable container experience"],
        ),
        generated_assets=GeneratedAssets(
            cv_bullets=["Led GenAI delivery for enterprise client"],
            recruiter_message="Hi, I'd love to discuss this role.",
            interview_prep_questions=["Why this role?"],
            interview_talking_points=["Enterprise delivery track record"],
        ),
    )


def test_summarize_pack_includes_fit_score_and_top_items():
    summary = summarize_pack(_sample_pack())

    assert "Fit score: 55/100" in summary
    assert "Enterprise stakeholder management" in summary
    assert "No Kubernetes experience" in summary


def test_format_history_caps_to_limit():
    history = [{"role": "user", "content": str(i)} for i in range(15)]

    formatted = format_history(history, limit=10)

    assert "0" not in formatted.split("\n")[0]
    assert formatted.count("user:") == 10


@pytest.mark.integration
def test_classify_intent_detects_job_url():
    intent = classify_intent(
        "hey can you check this JD out: https://example.com/jobs/123", has_active_pack=False
    )

    assert intent.action == "analyze_job"
    assert intent.job_url


@pytest.mark.integration
def test_classify_intent_detects_followup():
    intent = classify_intent("what does that fit score mean", has_active_pack=True)

    assert intent.action == "followup"
