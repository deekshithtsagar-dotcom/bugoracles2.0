"""
Test Case Generation Task Module
================================
This module defines the task for generating structured test cases from
extracted requirements. The task instructs the Test Case Agent on the
format and quality standards for test case documentation.
"""

from crewai import Task, Agent


class TestTask:
    """
    Task definition for generating test cases from requirements.
    
    This task guides the Test Case Agent to create comprehensive,
    well-structured test cases following industry standards and
    best practices for test documentation.
    """
    
    # Task description template with placeholder for requirements
    DESCRIPTION_TEMPLATE = """
    Generate comprehensive test cases based on the following extracted requirements:

    REQUIREMENTS AND ANALYSIS:
    {requirements}

    For each test case, provide:

    1. TEST CASE ID
       - Format: TC-XXX (e.g., TC-001, TC-002)
       - Use sequential numbering
       - Group related tests with prefixes when appropriate

    2. TITLE
       - Clear, descriptive title
       - Should indicate what is being tested
       - Keep concise but informative

    3. PRECONDITIONS
       - All required setup before execution
       - System state requirements
       - Test data requirements
       - User/role requirements

    4. STEPS
       - Numbered, sequential steps
       - Clear and unambiguous actions
       - Include expected intermediate results
       - One action per step

    5. EXPECTED RESULT
       - Clear success criteria
       - Measurable/observable outcomes
       - Include any relevant assertions

     6. PRIORITY
       - HIGH: Critical functionality, security, data integrity
       - MEDIUM: Important features, common user flows
       - LOW: Edge cases, cosmetic issues, rare scenarios

     7. PRIORITY REASON
         - 1 concise sentence
         - Explain why this priority was assigned
         - Explicitly mention risk/business impact

     Priority Assignment Logic (mandatory):
     - HIGH -> critical flows, payment, authentication, security, and historical bug hotspots
     - MEDIUM -> normal/common user flows with moderate impact
     - LOW -> edge, rare, and non-critical scenarios

    Test Case Guidelines:
    - Cover ALL functional requirements from the analysis
    - Include tests for EACH edge case identified
    - Include tests for EACH negative case
    - Ensure traceability to requirements (reference FR-XXX, EC-XXX, NC-XXX)
    - Prioritize based on risk and user impact
    - Make tests independent and repeatable
    """
    
    # Expected output format
    EXPECTED_OUTPUT = """
    A comprehensive test suite with structured test cases.
    Strictly follow this exact per-test markdown schema:
    
    ---
    ## Test Case: TC-001
    **Title:** [Descriptive test case title]
    
    **Priority:** [HIGH/MEDIUM/LOW]

    **Priority Reason:** [One-line risk-based reason]
    
    **Requirement Traceability:** [FR-XXX, EC-XXX, or NC-XXX]
    
    **Preconditions:**
    - [Precondition 1]
    - [Precondition 2]
    
    **Test Steps:**
    1. [Step 1 - Action]
    2. [Step 2 - Action]
    3. [Step 3 - Action]
    
    **Expected Result:**
    - [Expected outcome 1]
    - [Expected outcome 2]
    
    ---
    ## Test Case: TC-002
    ...
    
    (Continue for all test cases)
    
    ---
    ## Test Summary
    - Total Test Cases: [Number]
    - High Priority: [Number]
    - Medium Priority: [Number]
    - Low Priority: [Number]
    - Requirement Coverage: [Percentage or list]

    Do not omit Priority or Priority Reason for any test case.
    """
    
    @classmethod
    def create(cls, agent: Agent, requirements: str) -> Task:
        """
        Factory method to create a Test Case Generation task.
        
        Args:
            agent: The Agent that will execute this task
            requirements: The extracted requirements to generate tests for
            
        Returns:
            Task: Configured CrewAI Task for test case generation
        """
        # Format the description with the requirements
        description = cls.DESCRIPTION_TEMPLATE.format(requirements=requirements)
        
        # Create and return the task
        task = Task(
            description=description,
            expected_output=cls.EXPECTED_OUTPUT,
            agent=agent,
        )
        
        return task


def create_test_task(agent: Agent, requirements: str) -> Task:
    """
    Convenience function to create a Test Case Generation Task.
    
    Args:
        agent: The Test Case Agent to assign the task to
        requirements: The extracted requirements from requirement analysis
        
    Returns:
        Task: Configured test case generation task
    """
    return TestTask.create(agent, requirements)
