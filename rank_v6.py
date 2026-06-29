import json
import os
import subprocess
import pandas as pd
from tqdm import tqdm

# Auto-generate job_config.json from JD if needed
if os.path.exists("job_description.txt") and not os.path.exists("job_config.json"):
    print("job_config.json not found. Running jd_parser.py...")
    subprocess.run(["python", "jd_parser.py", "job_description.txt"])

print("Loading candidates...")

results = []

############################################################
# Load Job Configuration
############################################################

with open("job_config.json", "r", encoding="utf-8") as f:
    JOB_CONFIG = json.load(f)

############################################################
# Product Companies
############################################################

PRODUCT_COMPANIES = [
    "google", "amazon", "microsoft", "meta", "apple", "netflix",
    "adobe", "atlassian", "flipkart", "swiggy", "zomato", "phonepe",
    "razorpay", "cred", "ola", "sarvam", "krutrim", "openai",
    "anthropic", "cohere", "mistral", "perplexity", "meesho",
    "dunzo", "urban company", "zepto", "blinkit", "groww", "zerodha"
]

############################################################
# Service Companies
############################################################

SERVICE_COMPANIES = [
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "mindtree", "hcl", "tech mahindra", "mphasis",
    "hexaware", "ltimindtree", "persistent"
]

############################################################
# AI Titles
############################################################

AI_TITLES = {
    "senior ai engineer": 60,
    "ai engineer": 55,
    "machine learning engineer": 50,
    "ml engineer": 50,
    "research engineer": 45,
    "applied scientist": 45,
    "data scientist": 35,
    "backend engineer": 15
}

############################################################
# Bad Titles
############################################################

BAD_TITLES = [
    "marketing", "sales", "operations", "customer support",
    "accountant", "hr", "mechanical"
]

############################################################
# Career Keywords
############################################################

CAREER_KEYWORDS = [
    "rag", "retrieval", "ranking", "recommendation", "embedding",
    "embeddings", "vector", "vector search", "semantic search", "search",
    "machine learning", "deep learning", "llm", "production", "deployed",
    "evaluation", "ab testing", "offline evaluation", "online evaluation",
    "ndcg", "map", "mrr"
]

############################################################
# Semantic Alias Map
# Contextual Relevance — goes beyond keyword matching
# If candidate used "document retrieval pipeline" they understand RAG
############################################################

SKILL_ALIASES = {
    "rag": [
        "retrieval augmented", "document retrieval", "knowledge base qa",
        "qa pipeline", "grounded generation", "document qa", "retrieval pipeline"
    ],
    "llm": [
        "large language model", "foundation model", "gpt", "claude",
        "gemini", "mistral", "llama", "generative model"
    ],
    "embeddings": [
        "vector representation", "sentence transformer", "semantic embedding",
        "text embedding", "dense retrieval", "bi-encoder"
    ],
    "fine-tuning": [
        "lora", "qlora", "finetuned", "instruction tuning", "rlhf",
        "dpo", "sft", "supervised fine", "peft", "adapter"
    ],
    "mlops": [
        "model deployment", "model serving", "production ml", "ml pipeline",
        "model monitoring", "inference pipeline", "ci/cd ml"
    ],
    "vector search": [
        "faiss", "pinecone", "weaviate", "milvus", "qdrant", "chroma",
        "approximate nearest", "ann search", "hnsw"
    ],
    "deep learning": [
        "neural network", "transformer", "attention mechanism",
        "backpropagation", "convolutional", "lstm", "bert"
    ],
    "machine learning": [
        "predictive model", "ml model", "classification", "regression",
        "feature engineering", "model training", "scikit"
    ],
    "python": [
        "fastapi", "flask", "django", "pandas", "numpy", "pytorch",
        "tensorflow", "keras", "jupyter"
    ],
    "recommendation": [
        "collaborative filtering", "content based filtering", "matrix factorization",
        "personalization", "ranking model", "recsys"
    ]
}

############################################################
# Helper Functions
############################################################

def normalize(text):
    return str(text).lower().strip()


def contains_any(text, keywords):
    text = normalize(text)
    return any(keyword in text for keyword in keywords)


############################################################
# Skills Score
############################################################

def score_skills(skills):

    score = 0
    matched_required = []
    matched_preferred = []

    skill_set = {normalize(s) for s in skills}

    # Required Skills
    for skill in JOB_CONFIG["required_skills"]:
        if skill in skill_set:
            score += 20
            matched_required.append(skill)

    # Preferred Skills
    for skill in JOB_CONFIG["preferred_skills"]:
        if skill in skill_set:
            score += 10
            matched_preferred.append(skill)

    # Coverage Bonus
    required_total = len(JOB_CONFIG["required_skills"])
    if required_total > 0:
        coverage = len(matched_required) / required_total
        score += coverage * 50

    return score, matched_required, matched_preferred


############################################################
# Semantic Score
# Contextual Relevance — understands meaning beyond keywords
# Candidate who built "document retrieval pipeline" understands RAG
############################################################

def score_semantic(career, matched_required):

    score = 0
    semantic_matches = []

    career_text = " ".join(
        normalize(j.get("title", "") + " " + j.get("description", ""))
        for j in career
    )

    for skill in JOB_CONFIG["required_skills"]:

        # Skip if already matched via direct skill
        if skill in matched_required:
            continue

        aliases = SKILL_ALIASES.get(skill, [])

        for alias in aliases:
            if alias in career_text:
                score += 10
                semantic_matches.append(f"{skill}~{alias}")
                break

    return score, semantic_matches


############################################################
# Experience Score
############################################################

def score_experience(exp):

    if JOB_CONFIG["experience_best"][0] <= exp <= JOB_CONFIG["experience_best"][1]:
        return 60
    elif exp >= JOB_CONFIG["experience_min"]:
        return 40
    return 10


############################################################
# Title Score
############################################################

def score_title(title):

    title = normalize(title)
    score = 0

    for t, weight in AI_TITLES.items():
        if t in title:
            score += weight

    for bad in BAD_TITLES:
        if bad in title:
            score -= 30

    return score


############################################################
# Company Score
############################################################

def score_company(company):

    company = normalize(company)

    if any(c in company for c in PRODUCT_COMPANIES):
        return 30
    if any(c in company for c in SERVICE_COMPANIES):
        return 5
    return 10


############################################################
# Career Score
############################################################

def score_career(career):

    score = 0
    career_text = ""
    ai_jobs = 0

    for job in career:
        title = normalize(job.get("title", ""))
        desc = normalize(job.get("description", ""))
        career_text += title + " " + desc + " "

        if contains_any(title, JOB_CONFIG["preferred_titles"]):
            ai_jobs += 1

    for keyword in CAREER_KEYWORDS:
        if keyword in career_text:
            score += 8

    score += ai_jobs * 15

    return score


############################################################
# Recruiter Signals
############################################################

def score_signals(signals):

    score = 0

    if signals.get("open_to_work_flag"):
        score += 25

    score += signals.get("github_activity_score", 0) * 3
    score += signals.get("recruiter_response_rate", 0) * 50

    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        score += 30
    elif notice <= 60:
        score += 15
    else:
        score -= 10

    if signals.get("willing_to_relocate"):
        score += 15

    score += (signals.get("profile_completeness_score", 0) / 5)
    score += min(signals.get("saved_by_recruiters_30d", 0) * 2, 15)
    score += min(signals.get("profile_views_received_30d", 0) / 5, 10)

    return score


############################################################
# Reason Generator
############################################################

def generate_reasoning(profile, matched_required, matched_preferred,
                        semantic_matches, score):

    reason = []

    exp = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "")
    company = profile.get("current_company", "")

    if matched_required:
        reason.append(
            f"Matched {len(matched_required)}/{len(JOB_CONFIG['required_skills'])} "
            f"required skills ({', '.join(matched_required[:4])})"
        )

    if matched_preferred:
        reason.append(
            f"matched {len(matched_preferred)} preferred skills "
            f"({', '.join(matched_preferred[:3])})"
        )

    if semantic_matches:
        reason.append(
            f"semantic match on {', '.join([s.split('~')[0] for s in semantic_matches[:2]])}"
        )

    if exp:
        reason.append(f"{exp} years experience")

    if title:
        reason.append(f"currently {title}")

    if company:
        reason.append(f"at {company}")

    return "; ".join(reason) + f" | Score: {round(score, 2)}"


############################################################
# Read Candidates
############################################################

print("Reading candidate profiles...")

with open("candidates.jsonl", "r", encoding="utf-8") as f:

    for line in tqdm(f):

        candidate = json.loads(line)

        profile  = candidate.get("profile", {})
        signals  = candidate.get("redrob_signals", {})
        career   = candidate.get("career_history", [])

        # Candidate Skills
        skills = [
            normalize(s.get("name", ""))
            for s in candidate.get("skills", [])
        ]

        # Initialize Score
        score = 0

        # Skills
        skill_score, matched_required, matched_preferred = score_skills(skills)
        score += skill_score

        # Semantic — contextual relevance beyond keywords
        semantic_score, semantic_matches = score_semantic(career, matched_required)
        score += semantic_score

        # Experience
        experience = profile.get("years_of_experience", 0)
        score += score_experience(experience)

        # Current Title
        score += score_title(profile.get("current_title", ""))

        # Current Company
        score += score_company(profile.get("current_company", ""))

        # Career History
        score += score_career(career)

        # Recruiter Signals
        score += score_signals(signals)

        # Reasoning
        reasoning = generate_reasoning(
            profile, matched_required, matched_preferred,
            semantic_matches, score
        )

        # Save Candidate
        results.append({
            "candidate_id": candidate.get("candidate_id"),
            "score":        round(score, 2),
            "reasoning":    reasoning
        })

############################################################
# Convert to DataFrame
############################################################

df = pd.DataFrame(results)

df = df.sort_values(
    by=["score", "candidate_id"],
    ascending=[False, True]
)

df = df.head(100)
df = df.reset_index(drop=True)
df["rank"] = range(1, len(df) + 1)

df = df[["candidate_id", "rank", "score", "reasoning"]]

df.to_csv("submission.csv", index=False, encoding="utf-8")

############################################################
# Console Output
############################################################

print()
print("Loaded", len(df), "top candidates")
print()
print("Submission file created successfully!")
print()
print(df.head(10))