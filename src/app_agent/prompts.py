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

CHAT_INTENT_PROMPT = """
Classify what the user wants from their chat message.

- "analyze_job": they want a job posting analyzed. Extract the job description text
  verbatim into job_text if they pasted it, or the URL into job_url if they linked it.
- "followup": they are asking about a job analysis that already ran in this session
  (only valid if an application pack is already active).
- "chitchat": anything else (greetings, unrelated questions, etc).

An application pack is currently active: {has_active_pack}

User message:
{message}
"""

CHAT_FOLLOWUP_PROMPT = """
You are answering a follow-up question about a job application analysis you already
produced in this conversation. Answer conversationally and concisely. Do not restate
the whole pack — reference only what's relevant to the question.

Application pack:
{pack}

Recent conversation:
{history}

User's new message:
{message}
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
