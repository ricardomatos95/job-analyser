import pytest
from app_agent.nodes.input_loader import load_text_file
from app_agent.nodes.requirements_extractor import extract_requirements


@pytest.mark.integration
def test_extract_requirements_from_sample_job():
    text = load_text_file("examples/sample_job.txt")
    result = extract_requirements(text)

    assert result.job_title
    assert len(result.requirements) > 0
    assert "GenAI" in " ".join(result.keywords + [result.job_title])
