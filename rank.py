import json
import pandas as pd
from tqdm import tqdm

print("Loading candidates...")

results = []

# Skills required from the Job Description
AI_SKILLS = [
    "python",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "fine-tuning llms",
    "lora",
    "qlora",
    "pytorch",
    "tensorflow",
]

VECTOR_DB = [
    "milvus",
    "pinecone",
    "faiss",
    "qdrant",
    "weaviate",
    "elasticsearch",
    "opensearch",
]

SERVICE_COMPANIES = [
    "tcs",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "mindtree",
    "hcl",
    "tech mahindra",
]

PRODUCT_KEYWORDS = [
    "product",
    "startup",
    "recommendation",
    "ranking",
    "retrieval",
    "search",
]

with open("candidates.jsonl", "r", encoding="utf-8") as f:

    for line in tqdm(f):

        candidate = json.loads(line)

        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})

        score = 0

        #########################################
        # Skills
        #########################################

        skills = [
            s.get("name", "").lower()
            for s in candidate.get("skills", [])
        ]

        for skill in AI_SKILLS:
            if skill in skills:
                score += 8

        for db in VECTOR_DB:
            if db in skills:
                score += 10

        #########################################
        # Experience
        #########################################

        exp = profile.get("years_of_experience", 0)

        if 5 <= exp <= 9:
            score += 20
        elif exp >= 4:
            score += 10

        #########################################
        # Career Description
        #########################################

        career = candidate.get("career_history", [])

        career_text = ""

        for job in career:

            career_text += (
                job.get("title", "") + " " +
                job.get("description", "") + " "
            ).lower()

        important_words = [
            "retrieval",
            "ranking",
            "recommendation",
            "embedding",
            "vector",
            "rag",
            "search",
            "llm",
            "machine learning",
            "evaluation",
            "ndcg",
            "map",
            "mrr",
        ]

        for word in important_words:
            if word in career_text:
                score += 6

        #########################################
        # Product vs Service Company
        #########################################

        company = profile.get(
            "current_company", ""
        ).lower()

        if company in SERVICE_COMPANIES:
            score -= 8
        else:
            score += 8

        #########################################
        # Open to Work
        #########################################

        if signals.get("open_to_work_flag"):
            score += 10

        #########################################
        # Recruiter Response Rate
        #########################################

        score += signals.get(
            "recruiter_response_rate", 0
        ) * 20

        #########################################
        # GitHub Activity
        #########################################

        score += signals.get(
            "github_activity_score", 0
        )

        #########################################
        # Notice Period
        #########################################

        notice = signals.get(
            "notice_period_days", 90
        )

        if notice <= 30:
            score += 5
        elif notice > 60:
            score -= 5

        #########################################
        # Recent Activity
        #########################################

        score += min(
            signals.get(
                "profile_views_received_30d", 0
            ) / 10,
            5,
        )

        #########################################
        # Save
        #########################################

        results.append({
            "candidate_id": candidate["candidate_id"],
            "score": round(score, 2)
        })

print("Loaded", len(results), "candidates")

df = pd.DataFrame(results)

df = df.sort_values(
    by=["score", "candidate_id"],
    ascending=[False, True]
)

# Keep only Top 100
df = df.head(100)

# Add Rank
df["rank"] = range(1, 101)

# Dummy reasoning (will improve later)
df["reasoning"] = (
    "Strong AI profile with relevant skills, experience and recruiter signals."
)

# Final column order
df = df[
    [
        "candidate_id",
        "rank",
        "score",
        "reasoning",
    ]
]

df.to_csv(
    "submission.csv",
    index=False
)

print("Submission file created successfully!")
print(df.head(10))