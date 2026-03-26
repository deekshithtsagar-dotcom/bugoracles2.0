"""
Root Cause Prediction Task Module
=================================
This module defines the task for predicting likely failure points and root
causes before release using user story context, bug history, and risk analysis.
"""

from crewai import Task, Agent


class RootCauseTask:
    """Task definition for generating structured root cause predictions."""

    DESCRIPTION_TEMPLATE = """
    Predict likely pre-release failures and root causes for this feature.

    USER STORY:
    {user_story}

    HISTORICAL BUG DATA:
    {bug_history}

    RISK ANALYSIS:
    {risk_analysis}

    Requirements:
    - Correlate predicted failures with historical bug patterns.
    - Identify repeat patterns including auth, payment, state issues,
      session consistency, API failures, and integration boundaries.
    - Map each predicted failure to the most likely module.
    - Use practical, real-world reasoning grounded in likely engineering causes.

    Output constraints:
    - Provide minimum 3 and maximum 5 predictions.
    - Use the exact structure below for each prediction.
    - Keep each impact concise and production-oriented.
    """

    EXPECTED_OUTPUT = """
    Predicted Issue 1:
    - Module: [Module or subsystem]
    - Possible Root Cause: [Most likely technical cause]
    - Impact: [User/business impact]

    Predicted Issue 2:
    - Module: [Module or subsystem]
    - Possible Root Cause: [Most likely technical cause]
    - Impact: [User/business impact]

    Predicted Issue 3:
    - Module: [Module or subsystem]
    - Possible Root Cause: [Most likely technical cause]
    - Impact: [User/business impact]

    (Optionally include Issue 4 and 5 if justified.)
    """

    @classmethod
    def create(
        cls,
        agent: Agent,
        user_story: str,
        bug_history: str,
        risk_analysis: str,
    ) -> Task:
        """Factory method to create a Root Cause Prediction task."""
        description = cls.DESCRIPTION_TEMPLATE.format(
            user_story=user_story,
            bug_history=bug_history,
            risk_analysis=risk_analysis,
        )
        return Task(
            description=description,
            expected_output=cls.EXPECTED_OUTPUT,
            agent=agent,
        )


def create_root_cause_task(
    agent: Agent,
    user_story: str,
    bug_history: str,
    risk_analysis: str,
) -> Task:
    """Convenience function to create a Root Cause Prediction task."""
    return RootCauseTask.create(agent, user_story, bug_history, risk_analysis)
