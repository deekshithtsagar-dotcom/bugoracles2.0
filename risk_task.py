"""
Risk Analysis Task Module
=========================
This module defines the task for risk analysis based on user stories
and historical bug data. The task instructs the Risk Agent on how to
evaluate risks and produce risk assessments.
"""

from crewai import Task, Agent


class RiskTask:
    """
    Task definition for analyzing risks associated with a feature.
    
    This task guides the Risk Agent to evaluate the user story against
    bug history and produce a comprehensive risk assessment including
    risk score, explanation, and testing recommendations.
    """
    
    # Task description template with placeholders
    DESCRIPTION_TEMPLATE = """
    Perform a comprehensive risk analysis for the following feature:

    USER STORY:
    {user_story}

    HISTORICAL BUG DATA:
    {bug_history}

    Your risk analysis must include:

    1. RISK SCORE
       - Classify as: LOW, MEDIUM, or HIGH
         - Provide a numeric score from 0 to 100
       - Base your assessment on:
         * Complexity of the feature
         * Historical bug patterns in similar areas
         * Potential impact of failures
         * Integration points and dependencies

    2. RISK EXPLANATION
       - Detailed reasoning for the risk score
       - Specific risk factors identified
       - Correlation with historical bugs
       - Potential failure modes

    3. SUGGESTED TESTING DEPTH
       - Recommended testing intensity
       - Specific areas requiring focused testing
       - Suggested test types (unit, integration, E2E, performance)
       - Recommended regression scope

    Consider these risk factors:
    - Feature complexity and scope
    - Historical defect density in related areas
    - User impact if the feature fails
    - Business criticality
    - Technical debt and code quality concerns
    - External dependencies and integrations
    """
    
    # Expected output format
    EXPECTED_OUTPUT = """
    A structured risk assessment containing:
    
    ## Risk Score
    **Level:** [LOW/MEDIUM/HIGH]
    **Score:** [0-100]
    
    ## Risk Explanation
    ### Key Risk Factors:
    1. [Factor 1 with explanation]
    2. [Factor 2 with explanation]
    ...
    
    ### Historical Bug Correlation:
    - [Relevant bug pattern analysis]
    
    ### Potential Impact:
    - [Impact analysis if issues occur]
    
    ## Suggested Testing Depth
    ### Testing Intensity: [Light/Standard/Thorough/Extensive]
    
    ### Recommended Test Types:
    - [Test type 1]: [Rationale]
    - [Test type 2]: [Rationale]
    
    ### Focus Areas:
    1. [Area requiring special attention]
    2. [Area requiring special attention]
    
    ### Regression Recommendations:
    - [Scope and areas for regression testing]
    """
    
    @classmethod
    def create(cls, agent: Agent, user_story: str, bug_history: str) -> Task:
        """
        Factory method to create a Risk Analysis task.
        
        Args:
            agent: The Agent that will execute this task
            user_story: The user story text to analyze
            bug_history: Historical bug data for risk correlation
            
        Returns:
            Task: Configured CrewAI Task for risk analysis
        """
        # Format the description with the inputs
        description = cls.DESCRIPTION_TEMPLATE.format(
            user_story=user_story,
            bug_history=bug_history
        )
        
        # Create and return the task
        task = Task(
            description=description,
            expected_output=cls.EXPECTED_OUTPUT,
            agent=agent,
        )
        
        return task


def create_risk_task(agent: Agent, user_story: str, bug_history: str) -> Task:
    """
    Convenience function to create a Risk Analysis Task.
    
    Args:
        agent: The Risk Agent to assign the task to
        user_story: The user story text to analyze
        bug_history: Historical bug data for correlation
        
    Returns:
        Task: Configured risk analysis task
    """
    return RiskTask.create(agent, user_story, bug_history)
