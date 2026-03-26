"""
Risk Analysis Agent Module
==========================
This module defines the Risk Analysis Agent responsible for evaluating
risks associated with a feature based on user story and historical bug data.
"""

from crewai import Agent
from config import get_llm_instance, Config


class RiskAgent:
    """
    Agent specialized in analyzing and assessing risks for software features.
    
    This agent processes user stories and bug history to produce:
    - Risk Score: Classification as Low, Medium, or High
    - Risk Explanation: Detailed reasoning for the risk assessment
    - Suggested Testing Depth: Recommendations for testing intensity
    """
    
    # Agent role definition
    ROLE = "Senior Risk Analyst and QA Strategist"
    
    # Detailed goal for the agent
    GOAL = """
    Perform comprehensive risk analysis by evaluating user stories against 
    historical bug patterns. Identify potential risk areas, assess severity, 
    and recommend appropriate testing strategies to mitigate risks effectively.
    """
    
    # Backstory providing context for the agent's expertise
    BACKSTORY = """
    You are a risk analysis expert with deep experience in software quality 
    assurance and release management. With 12+ years in the industry, you have:
    
    - Led risk assessment for over 200 major software releases
    - Developed risk scoring frameworks used by Fortune 500 companies
    - Prevented numerous critical bugs from reaching production
    - Specialized in pattern recognition across bug histories
    
    Your approach combines quantitative analysis of historical data with 
    qualitative assessment of feature complexity. You excel at:
    
    - Correlating new features with historical bug patterns
    - Identifying high-risk areas based on code complexity and change scope
    - Recommending risk-appropriate testing strategies
    - Balancing thorough testing with release timelines
    
    You provide actionable insights that help teams focus testing efforts 
    where they matter most, ensuring efficient use of QA resources while 
    maintaining high quality standards.
    """
    
    @classmethod
    def create(cls) -> Agent:
        """
        Factory method to create and configure the Risk Analysis Agent.
        
        Returns:
            Agent: Configured CrewAI Agent instance for risk analysis
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


def create_risk_agent() -> Agent:
    """
    Convenience function to create a Risk Analysis Agent.
    
    This provides a simple interface for creating the agent without
    needing to instantiate the class.
    
    Returns:
        Agent: Configured Risk Analysis Agent
    """
    return RiskAgent.create()
