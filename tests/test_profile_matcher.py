from app_agent.nodes.profile_matcher import load_candidate_profile


def test_load_candidate_profile():
    profile = load_candidate_profile("candidate_profile.yaml")
    assert profile.name == "Ricardo Matos"
    assert "Enterprise AI deployment" in profile.strengths
