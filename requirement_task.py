"""
Requirement Task Module
=======================
This module defines the task for requirement extraction from user stories.
The task instructs the Requirement Agent on how to analyze user stories
and what output format to produce.
"""

from crewai import Task, Agent


class RequirementTask:
    """
    Task definition for extracting requirements from user stories.
    
    This task guides the Requirement Agent to analyze user story text
    and produce structured output including functional requirements,
    edge cases, negative cases, and test scenarios.
    """
    
    # Task description template with placeholder for user story
    DESCRIPTION_TEMPLATE = """
    Analyze the following user story and extract comprehensive requirements:

    USER STORY:
    {user_story}

    Your analysis must include:

    1. FUNCTIONAL REQUIREMENTS
       - List all core functional requirements
       - Each requirement should be specific and testable
       - Use "shall" statements (e.g., "The system shall...")

    2. EDGE CASES
       - Identify boundary conditions
       - Consider unusual but valid inputs
       - Think about timing and concurrency issues
       - Consider resource limits (max values, empty states)

    3. NEGATIVE CASES
       - Invalid input scenarios
       - Authentication/authorization failures
       - Error handling scenarios
       - Recovery from failures

    4. TEST SCENARIOS
       - High-level test scenarios covering the requirements
       - Include happy path scenarios
       - Include alternative flow scenarios
       - Consider integration points

    Be thorough and think from the perspective of:
    - End users (usability)
    - Developers (implementation)
    - Testers (testability)
    - Business stakeholders (value delivery)
    """
    
    # Expected output format
    EXPECTED_OUTPUT = """
    A structured analysis containing:
    
    ## Functional Requirements
    - FR-001: [Requirement description]
    - FR-002: [Requirement description]
    ...
    
    ## Edge Cases
    - EC-001: [Edge case description]
    - EC-002: [Edge case description]
    ...
    
    ## Negative Cases
    - NC-001: [Negative case description]
    - NC-002: [Negative case description]
    ...
    
    ## Test Scenarios
    - TS-001: [Scenario description]
    - TS-002: [Scenario description]
    ...
    """
    
    @classmethod
    def create(cls, agent: Agent, user_story: str) -> Task:
        """
        Factory method to create a Requirement extraction task.
        
        Args:
            agent: The Agent that will execute this task
            user_story: The user story text to analyze
            
        Returns:
            Task: Configured CrewAI Task for requirement extraction
        """
        # Format the description with the user story
        description = cls.DESCRIPTION_TEMPLATE.format(user_story=user_story)
        
        # Create and return the task
        task = Task(
            description=description,
            expected_output=cls.EXPECTED_OUTPUT,
            agent=agent,
        )
        
        return task


def create_requirement_task(agent: Agent, user_story: str) -> Task:
    """
    Convenience function to create a Requirement Task.
    
    Args:
        agent: The Requirement Agent to assign the task to
        user_story: The user story text to analyze
        
    Returns:
        Task: Configured requirement extraction task
    """
    return RequirementTask.create(agent, user_story)
