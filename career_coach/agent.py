#.\.venv\Scripts\activate      
# import datetime
# import os
# from dotenv import load_dotenv
# from google.adk.agents import Agent, LoopAgent
# from google.adk.tools import agent_tool

# # — Config & Environment —
# load_dotenv()
# MODEL = os.getenv("MODEL", "gemini-flash-latest")

# # — Sub-Agent 1: Job Analyzer —
# job_analyzer = Agent(
#     name="JobAnalyzer",
#     model=MODEL,
#     description="Analyzes a job description to extract core competencies and ATS keywords.",
#     instruction="""You are an expert technical recruiter and ATS specialist. 
# Analyze the provided job description and output a clear Markdown summary containing:
# - Target Role & Seniority
# - Must-Have Technical Stack & Tools
# - Core Engineering Responsibilities
# - 5-8 Critical Keywords required for ATS scanning

# Return ONLY the structured Markdown analysis.""",
#     output_key="job_analysis",
# )

# # — Sub-Agent 2: Resume Tailor —
# resume_tailor = Agent(
#     name="ResumeTailor",
#     model=MODEL,
#     description="Rewrites resume bullet points to align with target job requirements.",
#     instruction="""You are an expert technical resume writer. 
# Using the target requirements in `job_analysis` and the user's baseline background provided in the prompt, rewrite the resume experience section.

# Guidelines:
# - Use strong action verbs (e.g., Architected, Deployed, Engineered, Optimized).
# - Highlight relevant system architectures, frameworks, and pipelines matching the job.
# - Focus heavily on technical depth and practical execution.
# - Format strictly as professional Markdown bullet points under role headers.
# - Do NOT invent false experiences; reframe existing technical background to match the role.""",
#     output_key="tailored_resume",
# )


# class ATSValidationChecker(Agent):

#     def __init__(self):
#         super().__init__(
#             name="ATSValidationChecker",
#             model=MODEL,
#             description="Validates that the tailored resume passes ATS keyword and metrics checks.",
#             instruction="""Review the draft in `tailored_resume` against the keywords and tech stack in `job_analysis`.

# Check for:
# 1. Keyword Match: Are the primary technical tools from the job analysis explicitly integrated?
# 2. Quantifiable Impact: Do at least half of the bullet points include metrics, percentages, scalability numbers, or concrete outcomes?
# 3. Formatting: Is it clean, professional Markdown without fluff?

# If all 3 conditions are met, respond exactly with "ok".
# Otherwise, respond exactly with "retry" followed by a bulleted list of the missing keywords or bullets that lack quantifiable metrics.""",
#             output_key="validation_result",
#         )


# # — Self-Correcting Loop for Resume Tailoring —
# robust_resume_tailor = LoopAgent(
#     name="RobustResumeTailor",
#     description="Retries resume rewriting until it passes ATS keyword and quantifiable metrics validation.",
#     sub_agents=[resume_tailor, ATSValidationChecker()],
#     max_iterations=1,#3
# )

# # — Tools —
# analyzer_tool = agent_tool.AgentTool(agent=job_analyzer)
# tailor_tool = agent_tool.AgentTool(agent=robust_resume_tailor)

# # — Root Agent: Career Optimization Orchestrator —
# root_agent = Agent(
#     name="CareerCoach",
#     model=MODEL,
#     description="An automated job application and resume optimization engine.",
#     instruction=f"""You are an end-to-end AI Career Coach and Resume Engineering Orchestrator.
# When the user provides a Job Description and their Baseline Resume/Background:

# 1) Call `JobAnalyzer` (via analyzer_tool) to break down the job requirements and ATS keywords.
# 2) Call `RobustResumeTailor` (via tailor_tool) to generate an ATS-optimized, metrics-driven resume experience section.
# 3) Once the resume is validated and complete, synthesize both the job analysis and tailored resume to draft a compelling, highly customized 3-paragraph Cover Letter.
# 4) Output the final response cleanly separated into three sections:
#    - ## 📊 Job Analysis & ATS Keywords
#    - ## 📄 Tailored Resume Bullets (ATS Validated)
#    - ## ✉️ Customized Cover Letter

# Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
# """,
#     tools=[
#         analyzer_tool,
#         tailor_tool,
#     ],
# )

import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent

# — Config & Environment —
load_dotenv()
MODEL = os.getenv("MODEL", "gemini-flash-latest")

# — Step 1: Job Analyzer (Call 1) —
job_analyzer = Agent(
    name="JobAnalyzer",
    model=MODEL,
    description="Extracts core competencies and ATS keywords from the job description.",
    instruction="""You are an expert technical recruiter and ATS specialist. 
Analyze the user's provided job description and output a clear Markdown summary containing:
- Target Role & Seniority
- Must-Have Technical Stack & Tools
- Core Engineering Responsibilities
- 5-8 Critical Keywords required for ATS scanning

Return ONLY the structured Markdown analysis.""",
    output_key="job_analysis",
)

# — Step 2: Initial Resume Writer (Call 2) —
resume_writer = Agent(
    name="ResumeWriter",
    model=MODEL,
    description="Drafts the initial resume bullet points.",
    instruction="""You are a technical resume writer. 
Using the target requirements in `job_analysis` and the user's baseline background provided in the prompt, write a strong first draft of the resume experience section using professional Markdown bullet points.""",
    output_key="initial_resume_draft",
)

# — Step 3: The ATS Critic & Polisher (Call 3) —
# This REPLACES the LoopAgent validator! Instead of saying "retry" and causing 
# an infinite loop, this agent directly acts as the editor: it finds what is 
# missing and outputs the perfected version in one single pass.
ats_critic_and_polisher = Agent(
    name="ATSCriticAndPolisher",
    model=MODEL,
    description="Audits the initial draft against ATS rules and rewrites it to perfection.",
    instruction="""You are an elite ATS resume auditor and editor.
Review the draft in `initial_resume_draft` against the keywords and requirements in `job_analysis`.

Your Job: Rewrite and upgrade the bullet points into a FINAL, perfected version by enforcing these strict rules:
1. Keyword Injection: Ensure every primary tool and keyword from `job_analysis` is naturally woven into the bullets.
2. Quantifiable Impact: You MUST rewrite bullets so that at least 50% of them contain concrete metrics, percentages, scalability numbers, or time-saved data.
3. Strong Verbs: Start every bullet with high-impact action verbs (e.g., Architected, Deployed, Engineered, Optimized).

Output ONLY the upgraded, perfected Markdown resume experience section.""",
    output_key="tailored_resume",
)

# — Step 4: Cover Letter & Final Package Assembler (Call 4) —
cover_letter_writer = Agent(
    name="CoverLetterWriter",
    model=MODEL,
    description="Synthesizes the analysis and tailored resume into a cover letter and formats the final output.",
    instruction="""You are an executive career coach.
Using the analysis in `job_analysis` and the perfected resume in `tailored_resume`, write a compelling, customized 3-paragraph Cover Letter.

Once drafted, assemble and output the FINAL complete application package cleanly separated into these exact three sections:

## 📊 Job Analysis & ATS Keywords
[Insert the content from `job_analysis` here]

---

## 📄 Tailored Resume Bullets (ATS Validated)
[Insert the content from `tailored_resume` here]

---

## ✉️ Customized Cover Letter
[Insert your newly drafted 3-paragraph cover letter here]""",
    output_key="final_application_package",
)

# — Root Agent: Linear Sequential Pipeline —
# Runs Step 1 -> Step 2 -> Step 3 -> Step 4 deterministically.
# Exactly 4 API calls. Zero routing bloat. Zero loop traps.
root_agent = SequentialAgent(
    name="CareerCoach",
    description="An automated job application and resume optimization engine.",
    sub_agents=[
        job_analyzer,
        resume_writer,
        ats_critic_and_polisher,
        cover_letter_writer,
    ],
)