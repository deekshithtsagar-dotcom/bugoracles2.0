"""
Release Intelligence Module
==========================
Production-oriented decisioning and quality intelligence helpers for the
AI Release Testing platform.

This module provides:
- calculate_release_decision()
- assign_test_priority()
- compute_confidence_score()
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


def _normalize_risk_level(value: str) -> str:
    """Normalize free-form risk text into LOW/MEDIUM/HIGH."""
    text = (value or "").upper()
    if "HIGH" in text:
        return "HIGH"
    if "MEDIUM" in text:
        return "MEDIUM"
    return "LOW"


def _contains_critical_bugs(bug_history: str, risk_analysis: str = "") -> bool:
    """Detect whether critical bugs are present in historical inputs."""
    combined = f"{bug_history}\n{risk_analysis}".lower()
    return bool(
        re.search(r"severity\s*:\s*critical", combined)
        or re.search(r"\bcritical\b", combined)
    )


def extract_risk_level_and_score(risk_analysis: str) -> Tuple[str, int]:
    """Extract risk level and numeric score from risk analysis text.

    Returns:
        Tuple[str, int]: (risk_level, risk_score_0_to_100)
    """
    text = risk_analysis or ""
    level = _normalize_risk_level(text)

    score_match = re.search(r"risk\s*score[^\d]*(\d{1,3})", text, flags=re.IGNORECASE)
    if score_match:
        score = max(0, min(100, int(score_match.group(1))))
        return level, score

    fallback_map = {"LOW": 25, "MEDIUM": 60, "HIGH": 90}
    return level, fallback_map[level]


def calculate_release_decision(
    risk_score: str,
    bug_history: str,
    risk_analysis: str = "",
) -> Dict[str, object]:
    """Determine release readiness decision from risk and critical bug context.

    Decision rules:
    - HIGH risk -> BLOCK RELEASE
    - MEDIUM risk + critical bug present -> NEEDS MORE TESTING
    - LOW risk -> SAFE TO RELEASE
    """
    risk_level = _normalize_risk_level(risk_score)
    has_critical = _contains_critical_bugs(bug_history, risk_analysis)

    if risk_level == "HIGH":
        decision = "BLOCK RELEASE"
        color = "#ef4444"
        reasons = [
            "Overall risk score is HIGH, indicating significant release exposure.",
            "Potential production impact is substantial if unresolved issues remain.",
            "Release should be gated until high-risk areas are mitigated and retested.",
        ]
    elif risk_level == "MEDIUM" and has_critical:
        decision = "NEEDS MORE TESTING"
        color = "#f59e0b"
        reasons = [
            "Risk score is MEDIUM, requiring controlled validation before release.",
            "Critical defects are present in history/correlation and increase regression risk.",
            "Targeted high-priority and regression testing is needed before go-live.",
        ]
    elif risk_level == "LOW":
        decision = "SAFE TO RELEASE"
        color = "#10b981"
        reasons = [
            "Risk score is LOW with manageable failure probability.",
            "No blocking risk indicators were detected in the analysis.",
            "Standard release checks should be sufficient for deployment readiness.",
        ]
    else:
        decision = "NEEDS MORE TESTING"
        color = "#f59e0b"
        reasons = [
            "Risk posture is non-low and benefits from additional confidence-building tests.",
            "Evidence indicates further validation is required before production release.",
        ]

    return {
        "decision": decision,
        "color": color,
        "reason_bullets": reasons,
        "risk_level": risk_level,
        "critical_bugs_present": has_critical,
    }


def assign_test_priority(test_title: str, test_body: str = "", bug_history: str = "") -> Tuple[str, str]:
    """Assign risk-based priority and reason for a test case.

    Rules:
    - HIGH: critical flows, payment, auth, historical bug hot-spots
    - MEDIUM: normal/common flows
    - LOW: edge/rare/cosmetic scenarios
    """
    text = f"{test_title}\n{test_body}".lower()
    history = (bug_history or "").lower()

    high_keywords = [
        "payment", "checkout", "transaction", "auth", "login", "security", "permission",
        "critical", "inventory", "pricing", "session", "cart", "api",
    ]
    medium_keywords = ["search", "filter", "profile", "normal", "common", "standard", "update"]
    low_keywords = ["edge", "boundary", "rare", "cosmetic", "ui polish", "minor"]

    if any(word in text for word in high_keywords):
        return "HIGH", "Covers critical flow/security path or historically defect-prone area."

    if any(word in history for word in ["critical", "high", "bug-"]) and any(
        term in text for term in ["cart", "session", "price", "inventory", "auth", "api"]
    ):
        return "HIGH", "Mapped to historical bug hotspots with elevated failure impact."

    if any(word in text for word in low_keywords):
        return "LOW", "Focuses on edge/rare scenario with lower business impact."

    if any(word in text for word in medium_keywords):
        return "MEDIUM", "Validates important common flow without critical risk indicators."

    return "MEDIUM", "Defaulted to medium priority for standard functional coverage."


def summarize_test_priorities(test_cases: str, bug_history: str = "") -> Dict[str, object]:
    """Summarize generated test priority quality and distribution."""
    content = test_cases or ""
    blocks = re.split(r"\n---\n|\n##\s*Test Case", content)
    blocks = [block.strip() for block in blocks if block.strip()]

    distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0

    for block in blocks:
        if "TC-" not in block and "Test Case" not in block:
            continue

        total += 1
        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", block)
        declared_match = re.search(r"\*\*Priority:\*\*\s*(HIGH|MEDIUM|LOW)", block, re.IGNORECASE)

        title = title_match.group(1).strip() if title_match else ""
        if declared_match:
            priority = declared_match.group(1).upper()
        else:
            priority, _ = assign_test_priority(title, block, bug_history)

        distribution[priority] = distribution.get(priority, 0) + 1

    return {
        "total_test_cases": total,
        "distribution": distribution,
    }


def compute_confidence_score(
    user_story: str,
    bug_history: str,
    requirements: str,
    risk_analysis: str,
    test_cases: str,
) -> Dict[str, object]:
    """Compute AI confidence score (0-100) from input/output quality signals."""
    us = user_story or ""
    bh = bug_history or ""
    req = requirements or ""
    risk = risk_analysis or ""
    tests = test_cases or ""

    clarity = 0
    if len(us.strip()) > 120:
        clarity += 10
    if re.search(r"\bAs a\b", us, flags=re.IGNORECASE):
        clarity += 10
    if re.search(r"\bI want\b", us, flags=re.IGNORECASE) and re.search(r"\bso that\b", us, flags=re.IGNORECASE):
        clarity += 10

    acceptance = 0
    if re.search(r"acceptance criteria", us, flags=re.IGNORECASE):
        acceptance += 10
    bullet_count = len(re.findall(r"^\s*[-*]\s+", us, flags=re.MULTILINE))
    acceptance += min(15, bullet_count * 2)

    bug_quality = 0
    if len(bh.strip()) > 80:
        bug_quality += 5
    bug_quality += min(5, len(re.findall(r"BUG-\d{4}-\d+", bh, flags=re.IGNORECASE)))
    if re.search(r"severity\s*:", bh, flags=re.IGNORECASE):
        bug_quality += 5
    if re.search(r"root cause\s*:", bh, flags=re.IGNORECASE):
        bug_quality += 5

    completeness = 0
    if req.strip():
        completeness += 8
    if risk.strip():
        completeness += 8
    if tests.strip():
        completeness += 9

    tc_count = len(re.findall(r"TC-\d+", tests))
    if tc_count >= 5:
        completeness = min(25, completeness + 3)

    score = max(0, min(100, clarity + acceptance + bug_quality + completeness))

    if score > 80:
        category = "High Confidence"
    elif score >= 50:
        category = "Medium Confidence"
    else:
        category = "Low Confidence"

    factors: List[str] = [
        f"User story clarity contribution: {clarity}/30",
        f"Acceptance criteria contribution: {acceptance}/25",
        f"Bug history quality contribution: {bug_quality}/20",
        f"Output completeness contribution: {completeness}/25",
    ]

    return {
        "score": score,
        "category": category,
        "factors": factors,
    }


def build_risk_distribution(risk_level: str) -> Dict[str, int]:
    """Build a simple visualization-ready risk distribution based on final risk level."""
    level = _normalize_risk_level(risk_level)
    if level == "HIGH":
        return {"LOW": 20, "MEDIUM": 30, "HIGH": 50}
    if level == "MEDIUM":
        return {"LOW": 25, "MEDIUM": 50, "HIGH": 25}
    return {"LOW": 60, "MEDIUM": 30, "HIGH": 10}
