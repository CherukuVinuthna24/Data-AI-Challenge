import json
import pandas as pd
from tqdm import tqdm

print("Loading candidates...")

results = []

# AI Skills
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

# Vector Databases
VECTOR_DB = [
    "milvus",
    "pinecone",
    "faiss",
    "qdrant",
    "weaviate",
    "elasticsearch",
    "opensearch",
]

# Service Companies
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

IMPORTANT_WORDS = [
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

print("Reading candidate profiles...")

with open("candidates.jsonl", "r", encoding="utf-8") as f:

    for line in tqdm(f):

        candidate = json.loads(line)

        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})

        score = 0

        ################################################
        # Skills
        ################################################

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

        ################################################
        # Experience
        ################################################

        exp = profile.get(
            "years_of_experience",
            0
        )

        if 5 <= exp <= 9:
            score += 50
        elif 4 <= exp < 5:
            score += 30
        elif 9 < exp <= 12:
            score += 20
        else:
            score += 5

        ################################################
        # Career History
        ################################################

        career_text = ""

        for job in candidate.get(
            "career_history",
            []
        ):

            career_text += (
                job.get("title", "")
                + " "
                + job.get("description", "")
                + " "
            ).lower()

        for word in IMPORTANT_WORDS:
            if word in career_text:
                score += 6

        ################################################
        # Product vs Service Company
        ################################################

        company = profile.get(
            "current_company",
            ""
        ).lower()

        if any(
            c in company
            for c in SERVICE_COMPANIES
        ):
            score -= 25
        else:
            score += 20

        ################################################
        # Open To Work
        ################################################

        if signals.get(
            "open_to_work_flag"
        ):
            score += 25

        ################################################
        # Recruiter Response
        ################################################

        score += (
            signals.get(
                "recruiter_response_rate",
                0,
            )
            * 40
        )

        ################################################
        # GitHub
        ################################################

        score += (
            signals.get(
                "github_activity_score",
                0,
            )
            * 2
        )

        ################################################
        # Notice Period
        ################################################

        notice = signals.get(
            "notice_period_days",
            90,
        )

        if notice <= 30:
            score += 20
        elif notice <= 60:
            score += 10
        else:
            score -= 10

        ################################################
        # Relocation
        ################################################

        if signals.get(
            "willing_to_relocate"
        ):
            score += 15

        ################################################
        # Profile Completeness
        ################################################

        score += (
            signals.get(
                "profile_completeness_score",
                0,
            )
            / 10
        )

        ################################################
        # Saved by Recruiters
        ################################################

        score += min(
            signals.get(
                "saved_by_recruiters_30d",
                0,
            )
            * 2,
            10,
        )

        ################################################
        # Profile Views
        ################################################

        score += min(
            signals.get(
                "profile_views_received_30d",
                0,
            )
            / 10,
            5,
        )

        ################################################
        # Save
        ################################################

        results.append(
            {
                "candidate_id": candidate[
                    "candidate_id"
                ],
                "score": round(score, 2),
            }
        )

print(
    "Loaded",
    len(results),
    "candidates",
)

df = pd.DataFrame(results)
# Sort by score (descending), then candidate_id (ascending)
df = df.sort_values(
    by=["score", "candidate_id"],
    ascending=[False, True]
)

# Keep only Top 100
df = df.head(100).reset_index(drop=True)

# Add Rank
df["rank"] = range(1, len(df) + 1)

################################################
# Better Reasoning
################################################

reasonings = []

for _, row in df.iterrows():

    reason = (
        f"High match for Senior AI Engineer role "
        f"with strong AI skills, production experience, "
        f"recruiter engagement and overall score ({row['score']})."
    )

    reasonings.append(reason)

df["reasoning"] = reasonings

################################################
# Final Output
################################################

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
    index=False,
    encoding="utf-8"
)

print("\nSubmission file created successfully!\n")
print(df.head(10))
