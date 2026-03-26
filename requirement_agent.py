"""
Requirement Agent Module
========================
This module defines the Requirement Agent responsible for analyzing
user stories and extracting functional requirements, edge cases,
negative cases, and test scenarios.
"""

from crewai import Agent
from config import get_llm_instance, Config


class RequirementAgent:
    """
    Agent specialized in extracting and analyzing requirements from user stories.
    
    This agent processes user story text and produces:
    - Functional Requirements: Core functionality that must be implemented
    - Edge Cases: Boundary conditions and unusual scenarios
    - Negative Cases: Invalid inputs and error conditions
    - Test Scenarios: High-level testing approaches
    """
    
    # Agent role definition
    ROLE = "Senior Requirements Analyst"
    
    # Detailed goal for the agent
    GOAL = """
    Analyze user stories thoroughly to extract comprehensive requirements 
    including functional requirements, edge cases, negative test cases, 
    and detailed test scenarios. Ensure no critical requirement is missed.
    """
    
    # Backstory providing context for the agent's expertise
    BACKSTORY = """
    You are a seasoned requirements analyst with over 15 years of experience 
    in software development. You have worked on hundreds of projects across 
    various domains including fintech, healthcare, and e-commerce. 
    
    Your expertise lies in:
    - Breaking down complex user stories into atomic requirements
    - Identifying edge cases that developers often overlook
    - Anticipating negative scenarios and failure modes
    - Creating comprehensive test scenarios that ensure quality coverage
    
    You are known for your attention to detail and ability to think from 
    multiple perspectives: user, developer, tester, and business stakeholder.
    """
    
    @classmethod
    def create(cls) -> Agent:
        """
        Factory method to create and configure the Requirement Agent.
        
        Returns:
            Agent: Configured CrewAI Agent instance for requirement analysis
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


def create_requirement_agent() -> Agent:
    """
    Convenience function to create a Requirement Agent.
    
    This provides a simple interface for creating the agent without
    needing to instantiate the class.
    
    Returns:
        Agent: Configured Requirement Agent
    """
    return RequirementAgent.create()
