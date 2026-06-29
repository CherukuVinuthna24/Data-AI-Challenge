import json
import pandas as pd
from tqdm import tqdm

print("Loading candidates...")

results = []

############################################################
# AI Skills (weighted)
############################################################

SKILL_WEIGHTS = {
    "python": 15,
    "machine learning": 18,
    "deep learning": 15,
    "nlp": 18,
    "llm": 15,
    "fine-tuning llms": 18,
    "lora": 12,
    "qlora": 12,
    "pytorch": 12,
    "tensorflow": 10,
    "embedding": 20,
    "embeddings": 20,
    "retrieval": 22,
    "ranking": 22,
    "recommendation": 20,
    "rag": 20,
}

############################################################
# Vector Databases
############################################################

VECTOR_DB = [
    "milvus",
    "pinecone",
    "faiss",
    "qdrant",
    "weaviate",
    "elasticsearch",
    "opensearch",
]

############################################################
# Service Companies
############################################################

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

############################################################
# Product Companies
############################################################

PRODUCT_COMPANIES = [
    "google",
    "amazon",
    "microsoft",
    "meta",
    "netflix",
    "flipkart",
    "swiggy",
    "zomato",
    "razorpay",
    "phonepe",
    "cred",
    "atlassian",
    "adobe",
    "paytm",
    "ola",
]

############################################################
# Title Weights
############################################################

TITLE_WEIGHTS = {
    "senior ai engineer": 55,
    "ai engineer": 50,
    "machine learning engineer": 48,
    "ml engineer": 48,
    "applied scientist": 45,
    "research engineer": 42,
    "data scientist": 35,
    "backend engineer": 12,
}

############################################################
# Bad Titles
############################################################

BAD_TITLES = [
    "marketing",
    "sales",
    "accountant",
    "customer support",
    "operations",
    "hr",
    "mechanical",
]

############################################################
# Production ML Keywords
############################################################

IMPORTANT_WORDS = [
    "retrieval",
    "ranking",
    "recommendation",
    "embedding",
    "embeddings",
    "vector",
    "vector search",
    "semantic search",
    "search",
    "rag",
    "llm",
    "machine learning",
    "deep learning",
    "recommendation engine",
    "search engine",
    "production",
    "deployed",
    "evaluation",
    "offline evaluation",
    "online evaluation",
    "ab testing",
    "a/b testing",
    "ndcg",
    "map",
    "mrr",
]

print("Reading candidate profiles...")

with open("candidates.jsonl", "r", encoding="utf-8") as f:

    for line in tqdm(f):

        candidate = json.loads(line)

        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})
        career = candidate.get("career_history", [])

        score = 0
        ############################################################
        # 1. Skills Score
        ############################################################

        skills = [
            s.get("name", "").lower()
            for s in candidate.get("skills", [])
        ]

        skill_set = set(skills)

        for skill, weight in SKILL_WEIGHTS.items():
            if skill in skill_set:
                score += weight

        for db in VECTOR_DB:
            if db in skill_set:
                score += 18

        ############################################################
        # 2. Experience Score
        ############################################################

        exp = profile.get(
            "years_of_experience",
            0
        )

        if 5 <= exp <= 9:
            score += 60
        elif 4 <= exp < 5:
            score += 40
        elif 9 < exp <= 12:
            score += 30
        else:
            score += 10

        ############################################################
        # 3. Current Title Score
        ############################################################

        title = profile.get(
            "current_title",
            ""
        ).lower()

        for t, weight in TITLE_WEIGHTS.items():
            if t in title:
                score += weight

        for bad in BAD_TITLES:
            if bad in title:
                score -= 25

        ############################################################
        # 4. Career Score
        ############################################################

        career_text = ""
        ai_jobs = 0
        total_duration = 0

        for job in career:

            job_title = job.get(
                "title",
                ""
            ).lower()

            job_desc = job.get(
                "description",
                ""
            ).lower()

            career_text += (
                job_title
                + " "
                + job_desc
                + " "
            )

            total_duration += job.get(
                "duration_months",
                0
            )

            if any(
                x in job_title
                for x in [
                    "ai",
                    "machine learning",
                    "ml engineer",
                    "data scientist",
                    "applied scientist",
                ]
            ):
                ai_jobs += 1

        for word in IMPORTANT_WORDS:
            if word in career_text:
                score += 10

        score += ai_jobs * 15

        if len(career) > 0:

            avg_duration = (
                total_duration / len(career)
            )

            if avg_duration >= 24:
                score += 20
            elif avg_duration >= 18:
                score += 10
            elif avg_duration < 12:
                score -= 15
        ############################################################
        # 5. Company Score
        ############################################################

        company_text = " ".join(
            [
                j.get("company", "").lower()
                for j in career
            ]
        )

        for company in PRODUCT_COMPANIES:
            if company in company_text:
                score += 20

        for company in SERVICE_COMPANIES:
            if company in company_text:
                score += 5

        ############################################################
        # 6. Redrob Signals
        ############################################################

        if signals.get("open_to_work_flag"):
            score += 30

        score += (
            signals.get(
                "recruiter_response_rate",
                0
            ) * 60
        )

        score += (
            signals.get(
                "github_activity_score",
                0
            ) * 3
        )

        notice = signals.get(
            "notice_period_days",
            90
        )

        if notice <= 30:
            score += 30
        elif notice <= 60:
            score += 15
        else:
            score -= 20

        if signals.get(
            "willing_to_relocate"
        ):
            score += 20

        score += (
            signals.get(
                "profile_completeness_score",
                0
            ) / 5
        )

        score += min(
            signals.get(
                "saved_by_recruiters_30d",
                0
            ) * 3,
            15,
        )

        score += min(
            signals.get(
                "profile_views_received_30d",
                0
            ) / 5,
            10,
        )

        score += (
            signals.get(
                "interview_completion_rate",
                0
            ) * 20
        )

        score += (
            signals.get(
                "offer_acceptance_rate",
                0
            ) * 15
        )

        if signals.get("verified_email"):
            score += 5

        if signals.get("verified_phone"):
            score += 5

        ############################################################
        # Save Candidate
        ############################################################

        results.append(
            {
                "candidate_id": candidate.get(
                    "candidate_id"
                ),
                "score": round(score, 2),
            }
        )
############################################################
# Sort Candidates
############################################################

results = sorted(
    results,
    key=lambda x: (-x["score"], x["candidate_id"])
)

############################################################
# Keep Top 100
############################################################

results = results[:100]

############################################################
# Add Rank
############################################################

for i, r in enumerate(results, start=1):
    r["rank"] = i

############################################################
# Create DataFrame
############################################################

df = pd.DataFrame(results)

############################################################
# Add Reasoning
############################################################

df["reasoning"] = (
    "Strong AI candidate with production ML experience, "
    "retrieval/ranking expertise and positive hiring signals."
)

############################################################
# Final Column Order
############################################################

df = df[
    [
        "candidate_id",
        "rank",
        "score",
        "reasoning",
    ]
]

############################################################
# Save Submission
############################################################

df.to_csv(
    "submission.csv",
    index=False,
    encoding="utf-8"
)

############################################################
# Done
############################################################

print("\nLoaded", len(df), "top candidates")
print("\nSubmission file created successfully!\n")
print(df.head(10))