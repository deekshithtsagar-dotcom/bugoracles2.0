"""
Test Case Generation Agent Module
=================================
This module defines the Test Case Generation Agent responsible for
creating structured, comprehensive test cases from extracted requirements.
"""

from crewai import Agent
from config import get_llm_instance, Config


class TestCaseAgent:
    """
    Agent specialized in generating structured test cases from requirements.
    
    This agent processes extracted requirements and produces test cases with:
    - Test Case ID: Unique identifier for tracking
    - Title: Descriptive name for the test case
    - Preconditions: Required setup before test execution
    - Steps: Detailed execution steps
    - Expected Result: Clear success criteria
    - Priority: Importance level (High/Medium/Low)
    """
    
    # Agent role definition
    ROLE = "Senior Test Engineer and Test Architect"
    
    # Detailed goal for the agent
    GOAL = """
    Generate comprehensive, well-structured test cases that cover all 
    functional requirements, edge cases, and negative scenarios. Ensure 
    test cases are clear, actionable, and provide complete coverage while 
    being prioritized based on risk and importance.

    Output must be strictly structured and each test case must include:
    - Priority: HIGH / MEDIUM / LOW
    - Priority Reason: concise risk-based rationale
    """
    
    # Backstory providing context for the agent's expertise
    BACKSTORY = """
    You are an expert test engineer with 10+ years of experience in test 
    design and automation. Your background includes:
    
    - ISTQB Advanced Level certification in Test Analysis and Design
    - Experience across manual, automated, and exploratory testing
    - Expertise in boundary value analysis and equivalence partitioning
    - Track record of achieving 95%+ requirement coverage
    
    You have developed test suites for:
    - Financial trading platforms (high accuracy requirements)
    - Healthcare systems (regulatory compliance critical)
    - E-commerce platforms (user experience focused)
    - Real-time systems (performance critical)
    
    Your test cases are known for:
    - Crystal clear step-by-step instructions
    - Comprehensive precondition documentation
    - Precise expected results that eliminate ambiguity
    - Smart prioritization that maximizes defect detection early
    
    You follow industry best practices including:
    - IEEE 829 test documentation standards
    - Behavior-Driven Development (BDD) patterns when appropriate
    - Risk-based test prioritization
    - Traceability to requirements
    """
    
    @classmethod
    def create(cls) -> Agent:
        """
        Factory method to create and configure the Test Case Generation Agent.
        
        Returns:
            Agent: Configured CrewAI Agent instance for test case generation
        """
        # Get the LLM instance from config
        llm = get_llm_instance()
        
        # Create and return the agent with all configurations
        agent = Agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            llm=llm,
            verbose=Config.VERBOSE,
            allow_delegation=Config.ALLOW_DELEGATION,
            max_iter=Config.MAX_ITERATIONS,
        )
        
        return agent


def create_test_case_agent() -> Agent:
    """
    Convenience function to create a Test Case Generation Agent.
    
    This provides a simple interface for creating the agent without
    needing to instantiate the class.
    
    Returns:
        Agent: Configured Test Case Generation Agent
    """
    return TestCaseAgent.create()
