import json
import re
import sys
import os
import subprocess

# Auto-generate job_config.json from JD if needed
if os.path.exists("job_description.txt") and not os.path.exists("job_config.json"):
    print("job_config.json not found. Running jd_parser.py...")
    subprocess.run(["python", "jd_parser.py", "job_description.txt"])
SKILLS_DICT = {
    "required": [
        "python", "machine learning", "deep learning", "nlp", "fine-tuning llms",
        "lora", "pytorch", "tensorflow", "transformers", "bert", "gpt", "llm",
        "rag", "retrieval", "faiss", "pinecone", "weaviate", "embeddings",
        "fastapi", "docker", "kubernetes", "mlflow", "huggingface", "langchain",
        "sql", "git", "linux", "rest api", "aws", "gcp", "azure",
        "data engineering", "feature engineering", "model deployment", "mlops",
        "openai", "generative ai", "vector database", "prompt engineering",
        "classification", "regression", "recommendation", "computer vision",
        "reinforcement learning", "statistics", "probability", "a/b testing"
    ],
    "preferred": [
        "qlora", "rlhf", "dpo", "peft", "vllm", "triton", "ray", "spark",
        "airflow", "kafka", "redis", "elasticsearch", "grafana", "wandb",
        "langsmith", "llamaindex", "chroma", "milvus", "qdrant",
        "streamlit", "gradio", "flask", "celery", "postgresql", "mongodb",
        "terraform", "ci/cd", "github actions", "jenkins", "sagemaker",
        "vertex ai", "azure ml", "bedrock", "anthropic", "cohere",
        "open source", "research", "publication", "phd", "mtech"
    ]
}

SENIORITY_MAP = {
    "junior": ["junior", "associate", "entry", "fresher", "trainee", "intern", "0-2", "1-2"],
    "mid": ["mid", "engineer", "developer", "analyst", "2-4", "3-5", "2-5"],
    "senior": ["senior", "sr.", "sr ", "lead", "5+", "5-8", "6+", "5-10"],
    "staff": ["staff", "principal", "architect", "expert", "8+", "10+"],
    "manager": ["manager", "head", "director", "vp", "chief"]
}


def extract_experience(text: str) -> tuple:
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*(?:to|-)\s*(\d+)\s*years?',
        r'(\d+)\+\s*years?',
        r'minimum\s+(\d+)\s*years?',
        r'at least\s+(\d+)\s*years?',
        r'(\d+)\s*years?\s+(?:of\s+)?experience',
    ]
    for pattern in patterns:
        m = re.search(pattern, text_lower)
        if m:
            groups = [int(x) for x in m.groups() if x]
            if len(groups) == 2:
                return groups[0], groups[1]
            elif len(groups) == 1:
                return groups[0], groups[0] + 4
    return 3, 8


def extract_seniority(text: str) -> str:
    text_lower = text.lower()
    for level, keywords in SENIORITY_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return "mid"


def extract_skills(text: str) -> tuple:
    text_lower = text.lower()
    required, preferred = [], []

    # Split into sections
    req_section = ""
    pref_section = text_lower

    req_patterns = [
        r'(?:required|must.have|mandatory|minimum qualifications?)(.*?)(?:preferred|nice.to.have|good.to.have|bonus|$)',
        r'(?:requirements?|qualifications?)(.*?)(?:preferred|responsibilities|$)'
    ]
    for pattern in req_patterns:
        m = re.search(pattern, text_lower, re.DOTALL)
        if m:
            req_section = m.group(1)
            pref_section = text_lower.replace(req_section, "")
            break

    if not req_section:
        req_section = text_lower
        pref_section = ""

    for skill in SKILLS_DICT["required"]:
        if skill in req_section:
            required.append(skill)
        elif skill in pref_section:
            preferred.append(skill)

    for skill in SKILLS_DICT["preferred"]:
        if skill in req_section and skill not in required:
            preferred.append(skill)
        elif skill in pref_section and skill not in preferred:
            preferred.append(skill)

    # Deduplicate and cap
    required = list(dict.fromkeys(required))[:12]
    preferred = list(dict.fromkeys(preferred))[:10]

    return required, preferred


def extract_job_title(text: str) -> str:
    patterns = [
        r'(?:hiring|looking for|we are seeking|role:|position:|title:)\s*([^\n.]+)',
        r'^([^\n]{10,60}(?:engineer|scientist|analyst|developer|architect|manager|lead))',
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).strip()[:80]
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    return lines[0][:80] if lines else "AI/ML Engineer"


def extract_keywords(text: str, required: list, preferred: list) -> list:
    text_lower = text.lower()
    all_known = set(required + preferred)
    domain_keywords = [
        "retrieval augmented generation", "large language model",
        "neural network", "foundation model", "generative ai",
        "conversational ai", "production ml", "model serving",
        "inference optimization", "distributed training"
    ]
    found = []
    for kw in domain_keywords:
        if kw in text_lower and kw not in all_known:
            found.append(kw)
    return found[:6]


def parse_jd(jd_text: str) -> dict:
    title = extract_job_title(jd_text)
    seniority = extract_seniority(jd_text)
    exp_min, exp_max = extract_experience(jd_text)
    required_skills, preferred_skills = extract_skills(jd_text)
    keywords = extract_keywords(jd_text, required_skills, preferred_skills)

    config = {
        "job_title": title,
        "seniority": seniority,
        "experience": {"min": exp_min, "max": exp_max},
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "keywords": keywords,
        "scoring_weights": {
            "required_skill_match": 40,
            "preferred_skill_match": 20,
            "experience_fit": 15,
            "career_signals": 15,
            "recruiter_signals": 10
        }
    }
    return config


def main():
    if len(sys.argv) > 1:
        jd_file = sys.argv[1]
        with open(jd_file, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        print("Paste your Job Description below. Press Enter twice + Ctrl+Z (Windows) or Ctrl+D (Mac/Linux) when done:\n")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        jd_text = "\n".join(lines)

    if not jd_text.strip():
        print("Error: No job description provided.")
        sys.exit(1)

    print("\nParsing job description...")
    config = parse_jd(jd_text)

    with open("job_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\nJob Config Generated:")
    print(f"  Title      : {config['job_title']}")
    print(f"  Seniority  : {config['seniority']}")
    print(f"  Experience : {config['experience']['min']}–{config['experience']['max']} years")
    print(f"  Required   : {', '.join(config['required_skills']) or 'None detected'}")
    print(f"  Preferred  : {', '.join(config['preferred_skills']) or 'None detected'}")
    print(f"  Keywords   : {', '.join(config['keywords']) or 'None detected'}")
    print(f"\njob_config.json written successfully.")
    print(f"\nNext step: python rank_v6.py")


if __name__ == "__main__":
    main()