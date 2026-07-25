REQUIREMENTS_EXTRACTION_PROMPT = """
You are extracting structured job requirements from a job posting.

Return only accurate information from the posting. Do not invent requirements.

Job posting:
{job_text}
"""

PROFILE_MATCH_PROMPT = """
Compare the candidate profile against the job requirements.

Be honest. Mark weak or missing matches clearly. Where a retrieved proof point is
available for a requirement, prefer it as evidence over the general profile summary —
it is more specific and detailed.

Candidate profile:
{candidate_profile}

Retrieved proof points per requirement:
{retrieved_proof_points}

Job requirements:
{job_requirements}
"""

GAP_ANALYSIS_PROMPT = """
Analyze gaps between the candidate and the role.

Separate critical gaps from manageable gaps. Suggest mitigation strategies.

Match analysis:
{match_analysis}
"""

ASSET_GENERATION_PROMPT = """
Generate application assets based on the requirements, match analysis, and gap analysis.

Create:
1. Tailored CV bullets
2. Recruiter outreach message
3. Interview prep questions
4. Interview talking points

Requirements:
{job_requirements}

Match analysis:
{match_analysis}

Gap analysis:
{gap_analysis}
"""
