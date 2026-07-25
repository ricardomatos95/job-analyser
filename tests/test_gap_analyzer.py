import pytest
from app_agent.models import MatchAnalysis, MatchItem
from app_agent.nodes.gap_analyzer import analyze_gaps


@pytest.mark.integration
def test_analyze_gaps_from_match_analysis():
    match_analysis = MatchAnalysis(
        overall_fit_score=55,
        matches=[
            MatchItem(
                requirement="5+ years Kubernetes production experience",
                evidence="No direct Kubernetes experience found in profile.",
                match_strength="missing",
            ),
            MatchItem(
                requirement="Enterprise stakeholder management",
                evidence="Owned end-to-end Copilot delivery for a regulated enterprise environment.",
                match_strength="strong",
            ),
        ],
        strongest_selling_points=["Enterprise stakeholder management"],
    )

    result = analyze_gaps(match_analysis)

    assert result.critical_gaps or result.manageable_gaps
    assert isinstance(result.mitigation_strategy, list)
