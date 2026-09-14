from __future__ import annotations


CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "Programming": {
        "code",
        "coding",
        "programming",
        "python",
        "java",
        "javascript",
        "typescript",
        "fastapi",
        "django",
        "react",
        "github",
        "git",
        "api",
        "sql",
        "database",
    },
    "Fitness": {
        "gym",
        "workout",
        "exercise",
        "running",
        "run",
        "jog",
        "walk",
        "walking",
        "cycling",
        "yoga",
        "fitness",
    },
    "Learning": {
        "study",
        "learn",
        "learning",
        "read",
        "reading",
        "book",
        "course",
        "practice",
        "exam",
        "revision",
    },
    "Work": {
        "work",
        "meeting",
        "project",
        "report",
        "presentation",
        "office",
        "email",
        "deadline",
        "client",
    },
}


import re


def classify_task(title: str, description: str | None = None) -> str:
    text = f"{title} {description or ''}".lower()

    words = set(re.findall(r"\b[\w+#.-]+\b", text))

    scores: dict[str, int] = {
        category: 0
        for category in CATEGORY_KEYWORDS
    }

    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = len(words & keywords)

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Other"

    return best_category
