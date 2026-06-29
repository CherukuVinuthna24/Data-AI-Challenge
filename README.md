# AI Candidate Ranking Engine

## Overview

This project is an intelligent candidate ranking engine developed for the Redrob AI Hiring Hackathon.

The system processes over **100,000 candidate profiles** and ranks the **Top 100 candidates** for a given job description using a configurable, explainable, and modular scoring pipeline.

Unlike simple keyword matching, the engine combines multiple signals including skills, experience, job titles, career progression, recruiter activity, company background, and behavioral signals.

## How to Run

```bash
# Step 1 — Parse any Job Description
python jd_parser.py job_description.txt

# Step 2 — Rank 100K candidates
python rank_v6.py

# Step 3 — Validate output
python validate_submission.py submission.csv
```

Paste any job description into `job_description.txt`. The system automatically extracts required skills, preferred skills, experience range, and seniority — no manual configuration needed.

## Full Pipeline

```
job_description.txt
        │
        ▼
jd_parser.py
Auto-extracts: required skills, preferred skills,
experience range, seniority, job title, keywords
        │
        ▼
job_config.json
Dynamic configuration — no hardcoding
        │
        ▼
rank_v6.py — Intelligent Candidate Ranker
Processes 100,000 candidates in ~16 seconds
        │
   ┌────┴────────────────────────────────┐
   ▼          ▼             ▼            ▼
Skill      Career        Company    Recruiter
Score      Score         Score      Signals
   │          │             │            │
   └────┬─────┴─────────────┴────────────┘
        ▼
  Final Weighted Score
        │
        ▼
  Explainable Top-100
        │
        ▼
  submission.csv
```


## Architecture

```
Job Description (raw text)
        │
        ▼
┌───────────────────┐
│   jd_parser.py    │  ← Deep Job Understanding
│                   │
│ • Required Skills │
│ • Preferred Skills│
│ • Experience      │
│ • Seniority       │
│ • Keywords        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  job_config.json  │  ← Dynamic Configuration
└────────┬──────────┘
         │
         ▼
┌───────────────────────────────────────────┐
│              rank_v6.py                   │  ← Ranking Engine
│                                           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │  Skill   │  │  Career  │  │ Signal │  │
│  │  Score   │  │  Score   │  │ Score  │  │
│  │          │  │          │  │        │  │
│  │ Required │  │ AI Titles│  │ GitHub │  │
│  │ Preferred│  │ Companies│  │ Notice │  │
│  │ Coverage │  │ Keywords │  │ OpenTo │  │
│  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       └─────────────┴────────────┘        │
│                     │                     │
│              Final Score                  │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Explainable Top-100   │
         │                        │
         │  Matched 6/8 required  │
         │  skills (Python, NLP,  │
         │  LLM, PyTorch);        │
         │  matched 4 preferred;  │
         │  7.2 years experience; │
         │  Senior AI Engineer    │
         └────────────────────────┘
                      │
                      ▼
               submission.csv
```

---

## Sample Output

```
candidate_id    rank    score     reasoning
CAND_0002025     1     845.06    Matched 4/8 required skills (python, deep learning,
                                 nlp, lora); matched 3 preferred skills (rag,
                                 embeddings, faiss); 7.2 years experience;
                                 currently Senior AI Engineer; at Sarvam AI
CAND_0039754     2     804.67    Matched 5/8 required skills (python, machine
                                 learning, deep learning, lora, pytorch); matched
                                 4 preferred skills (rag, retrieval, embeddings);
                                 6.8 years experience; currently ML Engineer
```

---

## Project Evolution

```
rank.py
Basic keyword ranking
        ↓
rank_v3.py
Improved scoring
        ↓
rank_v4.py
Titles + Companies + Recruiter Signals
        ↓
rank_v5.py
Weighted Intelligent Ranking Engine
        ↓
rank_v6.py
JD-aware Modular Scoring Engine
        ↓
jd_parser.py
Deep Job Understanding — auto-configure from any JD
```

---

## Features

- **Deep Job Understanding** — jd_parser.py reads any raw job description and extracts structured config automatically
- **Dynamic Configuration** — job_config.json drives the entire scorer, no hardcoding
- **Required vs Preferred skill scoring** — with coverage bonus
- **AI title matching** — weighted by seniority and relevance
- **Experience-based scoring** — with optimal range detection
- **Career progression analysis** — keyword and title signals across full history
- **Product vs Service company scoring** — Google, Flipkart, Swiggy ranked higher
- **Recruiter behavioral signals** — GitHub activity, notice period, open to work, profile views
- **Explainable reasoning** — every candidate gets a human-readable explanation
- **Processes 100K candidates in ~16 seconds**

---

## Project Structure

```
redrob_hackathon/
│
├── jd_parser.py           ← Parse any JD → job_config.json
├── rank_v6.py             ← Main ranking engine
├── job_config.json        ← Auto-generated job configuration
├── job_description.txt    ← Paste your JD here
├── submission.csv         ← Final ranked output
├── validate_submission.py ← Validation script
├── requirements.txt
└── README.md
```

---

## Scoring Weights

| Component | Signal | Weight |
|---|---|---|
| Skill Score | Required skill match | 20 pts each |
| Skill Score | Preferred skill match | 10 pts each |
| Skill Score | Coverage bonus | up to 50 pts |
| Experience | Optimal range match | 60 pts |
| Title | Senior AI Engineer | 60 pts |
| Company | Product company | 30 pts |
| Career | Domain keywords | 8 pts each |
| Signals | Open to work | 25 pts |
| Signals | Short notice period | 30 pts |
| Signals | GitHub activity | up to 30 pts |

---

## Technologies Used

- Python
- Pandas
- tqdm

---

## Performance

- Candidates Processed: 100,000
- Output: Top 100 Candidates
- Runtime: ~15–16 seconds
- Explainable reasoning generated for every candidate

---

## Future Improvements

- Sentence Transformer embeddings
- Semantic candidate matching
- Cosine similarity scoring
- Hybrid AI + Rule-based ranking
- LLM-powered candidate explanations

---

## Author

Developed as part of the Redrob AI Hiring Hackathon.