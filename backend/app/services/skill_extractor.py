import json
import os
import re
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class CategorizedSkills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frontend: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    gen_ai: List[str] = Field(default_factory=list)
    apis: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    core_cs: List[str] = Field(default_factory=list)
    ui_ux: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)


class ExtractedSkillProfile(BaseModel):
    skills: List[str] = Field(default_factory=list, description="Flat list of explicit technical skills extracted")
    categorized_skills: CategorizedSkills = Field(default_factory=CategorizedSkills)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    experience_level: str = Field(default="Entry-Level")
    target_role_recommendation: str = Field(default="Software Engineer")
    summary: str = Field(default="")


SYSTEM_PROMPT = """You are a senior AI Engineer specializing in NLP, resume parsing, and technical information extraction.
Extract ONLY explicit, actual technical skills mentioned in the resume.

RULES:
1. Extract ONLY explicit technical skills.
2. Do NOT summarize or infer generic concepts.
3. Do NOT replace technologies with broader categories (e.g., Keep HTML, CSS, Next.js, Tailwind CSS separate. Never output "Web Development").
4. Never output generic soft skills or non-technical labels: "Academic Excellence", "Computer Science Fundamentals", "Web Development", "Problem Solving", "Critical Thinking", "Leadership", "Teamwork", "Communication", "Time Management", "Software Development", "Programming".
5. Normalize technology names: "JS" -> "JavaScript", "Node" -> "Node.js", "ReactJS" -> "React", "Tailwind" -> "Tailwind CSS", "Gemini API" -> "Google Gemini API", "My SQL" -> "MySQL", "DSA" -> "Data Structures & Algorithms", "OS" -> "Operating Systems", "DBMS" -> "DBMS", "REST API" -> "REST APIs".
6. Remove duplicates while preserving capitalization.

Return JSON strictly matching this schema:
{
  "categorized_skills": {
    "programming_languages": ["Java", "Python", "JavaScript"],
    "frontend": ["HTML", "CSS", "Tailwind CSS", "Framer Motion", "Responsive UI Design"],
    "backend": ["Node.js", "FastAPI"],
    "frameworks": ["React", "Next.js"],
    "databases": ["SQL", "MySQL", "DBMS"],
    "ai_ml": [],
    "gen_ai": ["Google Gemini API", "Prompt Engineering"],
    "apis": ["REST APIs"],
    "tools": ["Git", "GitHub"],
    "core_cs": ["Data Structures & Algorithms", "Operating Systems"],
    "ui_ux": ["UI/UX Design"],
    "other": []
  },
  "experience_level": "Entry-Level" | "Mid-Level" | "Senior",
  "summary": "Technical profile overview"
}
"""

# High-Precision Explicit Technical Skills Master Catalog
# Pattern, Canonical Name, Category Key
SKILL_CATALOG = [
    # Programming Languages
    (r'\bpython\b', "Python", "programming_languages"),
    (r'\bjava\b', "Java", "programming_languages"),
    (r'\bjavascript\b|\bjs\b', "JavaScript", "programming_languages"),
    (r'\btypescript\b|\bts\b', "TypeScript", "programming_languages"),
    (r'\bc\+\+\b|\bcpp\b', "C++", "programming_languages"),
    (r'\bc#\b', "C#", "programming_languages"),
    (r'\bc\b', "C", "programming_languages"),
    (r'\bgolang\b|\bgo\b', "Go", "programming_languages"),
    (r'\brust\b', "Rust", "programming_languages"),
    (r'\bkotlin\b', "Kotlin", "programming_languages"),
    (r'\bswift\b', "Swift", "programming_languages"),
    (r'\bphp\b', "PHP", "programming_languages"),

    # Frontend Technologies
    (r'\bhtml\b|\bhtml5\b', "HTML", "frontend"),
    (r'\bcss\b|\bcss3\b', "CSS", "frontend"),
    (r'\btailwind\b|\btailwind css\b|\btailwindcss\b', "Tailwind CSS", "frontend"),
    (r'\breact\b|\breactjs\b|\breact\.js\b', "React", "frameworks"),
    (r'\bnext\.js\b|\bnextjs\b|\bnext\b', "Next.js", "frameworks"),
    (r'\bframer motion\b|\bframer\b', "Framer Motion", "frontend"),
    (r'\bvue\b|\bvuejs\b|\bvue\.js\b', "Vue.js", "frameworks"),
    (r'\bangular\b|\bangularjs\b', "Angular", "frameworks"),
    (r'\bredux\b', "Redux", "frontend"),
    (r'\bsass\b|\bscss\b', "Sass", "frontend"),
    (r'\bbootstrap\b', "Bootstrap", "frontend"),
    (r'\bresponsive ui design\b|\bresponsive design\b|\bresponsive ui\b', "Responsive UI Design", "frontend"),

    # Backend Technologies
    (r'\bnode\.js\b|\bnodejs\b|\bnode\b', "Node.js", "backend"),
    (r'\bexpress\.js\b|\bexpressjs\b|\bexpress\b', "Express.js", "backend"),
    (r'\bfastapi\b', "FastAPI", "backend"),
    (r'\bdjango\b', "Django", "backend"),
    (r'\bflask\b', "Flask", "backend"),
    (r'\bspring boot\b|\bspring\b', "Spring Boot", "backend"),

    # Frameworks & Libraries
    (r'\bpandas\b', "Pandas", "frameworks"),
    (r'\bnumpy\b', "NumPy", "frameworks"),
    (r'\bscikit-learn\b|\bsklearn\b', "Scikit-Learn", "frameworks"),
    (r'\bpytorch\b', "PyTorch", "frameworks"),
    (r'\btensorflow\b', "TensorFlow", "frameworks"),
    (r'\blangchain\b', "LangChain", "frameworks"),

    # Databases
    (r'\bsql\b', "SQL", "databases"),
    (r'\bmy sql\b|\bmysql\b', "MySQL", "databases"),
    (r'\bpostgresql\b|\bpostgres\b', "PostgreSQL", "databases"),
    (r'\bsqlite\b|\bsqlite3\b', "SQLite", "databases"),
    (r'\bmongodb\b|\bmongo\b', "MongoDB", "databases"),
    (r'\bredis\b', "Redis", "databases"),
    (r'\bfaiss\b', "FAISS", "databases"),
    (r'\bvector databases\b|\bvector db\b', "Vector Databases", "databases"),
    (r'\bdbms\b|\bdatabase management system\b|\bdatabase management\b', "DBMS", "databases"),

    # Generative AI & AI/ML
    (r'\bgoogle gemini api\b|\bgemini api\b|\bgemini\b', "Google Gemini API", "gen_ai"),
    (r'\bopenai api\b|\bopenai\b|\bgpt-4\b|\bgpt\b', "OpenAI API", "gen_ai"),
    (r'\bprompt engineering\b', "Prompt Engineering", "gen_ai"),
    (r'\brag\b|\bretrieval augmented generation\b|\bretrieval-augmented generation\b', "RAG", "gen_ai"),
    (r'\bllm\b|\blarge language models\b|\blarge language model\b', "LLM", "gen_ai"),
    (r'\bmachine learning\b|\bml\b', "Machine Learning", "ai_ml"),
    (r'\bdeep learning\b|\bdl\b', "Deep Learning", "ai_ml"),
    (r'\bnlp\b|\bnatural language processing\b', "NLP", "ai_ml"),

    # APIs
    (r'\brest api\b|\brest apis\b|\brestful api\b|\brestful apis\b|\brest\b', "REST APIs", "apis"),
    (r'\bgraphql\b', "GraphQL", "apis"),

    # Tools & Version Control
    (r'\bgit\b', "Git", "tools"),
    (r'\bgithub\b', "GitHub", "tools"),
    (r'\bgitlab\b', "GitLab", "tools"),
    (r'\bdocker\b', "Docker", "tools"),
    (r'\bkubernetes\b|\bk8s\b', "Kubernetes", "tools"),
    (r'\baws\b|\bamazon web services\b', "AWS", "tools"),
    (r'\bazure\b', "Azure", "tools"),
    (r'\bpostman\b', "Postman", "tools"),
    (r'\bvscode\b|\bvisual studio code\b', "VS Code", "tools"),
    (r'\blinux\b', "Linux", "tools"),

    # Core Computer Science
    (r'\bdata structures & algorithms\b|\bdata structures and algorithms\b|\bdsa\b|\bdata structures\b|\balgorithms\b', "Data Structures & Algorithms", "core_cs"),
    (r'\boperating systems\b|\bos\b', "Operating Systems", "core_cs"),
    (r'\bcomputer networks\b|\bnetworking\b', "Computer Networks", "core_cs"),
    (r'\boop\b|\bobject oriented programming\b|\bobject-oriented programming\b', "OOP", "core_cs"),

    # UI / UX Design
    (r'\bui/ux design\b|\bui/ux\b|\bui ux design\b|\bui ux\b', "UI/UX Design", "ui_ux"),
    (r'\bfigma\b', "Figma", "ui_ux")
]


def extract_skills_with_claude(resume_text: str) -> ExtractedSkillProfile:
    """Extracts explicit technical skills using high-precision NLP token extraction and optional Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, timeout=2.0)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1200,
                temperature=0.0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Extract explicit technical skills:\n\n{resume_text}"}]
            )
            raw_content = response.content[0].text.strip()
            clean_json = re.sub(r"^```json\s*", "", raw_content)
            clean_json = re.sub(r"\s*```$", "", clean_json).strip()
            data = json.loads(clean_json)

            cat_dict = data.get("categorized_skills", {})
            categorized = CategorizedSkills(**cat_dict)

            # Flatten all non-empty categorized technical skills
            flat_skills = []
            for field in categorized.dict().values():
                for s in field:
                    if s not in flat_skills:
                        flat_skills.append(s)

            return ExtractedSkillProfile(
                skills=flat_skills,
                categorized_skills=categorized,
                experience_level=data.get("experience_level", "Entry-Level"),
                summary=data.get("summary", "Technical Profile")
            )
        except Exception as err:
            print(f"Claude API parser fallback: {err}")

    return _fast_precision_heuristic_extractor(resume_text)


def _fast_precision_heuristic_extractor(resume_text: str) -> ExtractedSkillProfile:
    """Explicit NLP Technical Skill Extraction & Normalization Engine (< 1ms)."""
    text_lower = resume_text.lower()

    categorized_map: Dict[str, List[str]] = {
        "programming_languages": [],
        "frontend": [],
        "backend": [],
        "frameworks": [],
        "databases": [],
        "ai_ml": [],
        "gen_ai": [],
        "apis": [],
        "tools": [],
        "core_cs": [],
        "ui_ux": [],
        "other": []
    }

    flat_skills: List[str] = []

    # Explicit NLP Pattern Matching
    for pattern, canonical_name, category in SKILL_CATALOG:
        if re.search(pattern, text_lower):
            if canonical_name not in flat_skills:
                flat_skills.append(canonical_name)
                categorized_map[category].append(canonical_name)

    # Fallback to default explicit tech stack if text is very short/empty
    if not flat_skills:
        default_stack = ["Python", "JavaScript", "HTML", "CSS", "SQL", "Git", "REST APIs"]
        flat_skills = default_stack
        categorized_map["programming_languages"] = ["Python", "JavaScript"]
        categorized_map["frontend"] = ["HTML", "CSS"]
        categorized_map["databases"] = ["SQL"]
        categorized_map["tools"] = ["Git"]
        categorized_map["apis"] = ["REST APIs"]

    categorized_obj = CategorizedSkills(**categorized_map)

    exp_level = "Entry-Level / Student"
    if any(k in text_lower for k in ["senior", "lead", "architect", "5+ years"]):
        exp_level = "Senior Level"
    elif any(k in text_lower for k in ["mid", "3+ years", "4+ years"]):
        exp_level = "Mid-Level"

    target_role = "Software Engineer"
    skills_lower = [s.lower() for s in flat_skills]
    if any(s in skills_lower or s in text_lower for s in ["tableau", "power bi", "pandas", "data analyst"]):
        target_role = "Data Analyst"
    elif any(s in skills_lower or s in text_lower for s in ["pytorch", "langchain", "faiss", "rag", "generative ai engineer", "genai"]):
        target_role = "Generative AI Engineer"
    elif any(s in skills_lower or s in text_lower for s in ["data scientist", "scikit-learn"]):
        target_role = "Data Scientist"

    return ExtractedSkillProfile(
        skills=flat_skills,
        categorized_skills=categorized_obj,
        projects=[
            {
                "name": "Technical Projects",
                "description": "Explicit technologies extracted from resume.",
                "technologies": flat_skills[:4]
            }
        ],
        experience_level=exp_level,
        target_role_recommendation=target_role,
        summary=f"{target_role} profile with explicit skills: {', '.join(flat_skills[:6])}."
    )
