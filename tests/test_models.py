from app_agent.models import JobRequirement, JobRequirements


def test_job_requirements_model_accepts_valid_data():
    item = JobRequirement(
        category="technical",
        requirement="Build agentic AI workflows using LangGraph",
        importance="must_have",
    )

    requirements = JobRequirements(
        job_title="Forward Deployed Engineer",
        company="Google",
        location="London",
        seniority="Senior",
        requirements=[item],
        responsibilities=["Work with customers to deploy GenAI solutions"],
        keywords=["LangGraph", "RAG", "Vertex AI"],
    )

    assert requirements.job_title == "Forward Deployed Engineer"
    assert requirements.requirements[0].category == "technical"
