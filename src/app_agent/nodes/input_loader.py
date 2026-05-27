from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from app_agent.models import JobInput


def load_job_input(job_input: JobInput) -> str:
    if job_input.source_type == "text":
        return job_input.content.strip()

    response = httpx.get(job_input.content, timeout=20.0, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:15000]


def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
