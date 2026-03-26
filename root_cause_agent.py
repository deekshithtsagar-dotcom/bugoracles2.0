"""
Root Cause Prediction Agent Module
==================================
This module defines the Root Cause Prediction Agent responsible for
predicting likely pre-release failure points from requirements context,
risk analysis, and historical bug patterns.
"""

from crewai import Agent
from config import get_llm_instance, Config


class RootCauseAgent:
    """
    Agent specialized in predicting likely failure points and root causes.

    This agent correlates user story scope, historical bug history, and risk
    analysis outputs to provide structured pre-release issue predictions.
    """

    ROLE = "Senior SDET Root Cause Analyst"

    GOAL = """
    Predict high-probability failure points before release by correlating
    historical bug patterns, feature risk signals, and system behavior.

    Always produce 3-5 structured predictions with module mapping,
    probable root cause, and production impact.
    """

    BACKSTORY = """
    You are a release reliability specialist with deep expertise in production
    incident prevention and defect trend analysis. You have led RCA reviews for
    large-scale web platforms across authentication, payments, state management,
    and distributed APIs.

    You are known for practical predictions that help QA and engineering teams
    prevent incidents before deployment by targeting likely module-level failure
    patterns.
    """

    @classmethod
    def create(cls) -> Agent:
        """Factory method to create and configure the Root Cause Agent."""
        llm = get_llm_instance()
        return Agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            llm=llm,
            verbose=Config.VERBOSE,
            allow_delegation=Config.ALLOW_DELEGATION,
            max_iter=Config.MAX_ITERATIONS,
        )


def create_root_cause_agent() -> Agent:
    """Convenience function to create a Root Cause Prediction Agent."""
    return RootCauseAgent.create()
