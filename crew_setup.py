"""
Crew Setup Module
=================
Orchestrates all agents using CrewAI.
Enhanced with RAG - automatically retrieves relevant context
from ChromaDB before running agents.
"""

from crewai import Crew, Process
from typing import Dict, Any

# Import agent creators
from agents.requirement_agent import create_requirement_agent
from agents.risk_agent import create_risk_agent
from agents.test_case_agent import create_test_case_agent
from agents.root_cause_agent import create_root_cause_agent

# Import task creators
from tasks.requirement_task import create_requirement_task
from tasks.risk_task import create_risk_task
from tasks.test_task import create_test_task
from tasks.root_cause_task import create_root_cause_task

from config import Config
from release_intelligence import (
    build_risk_distribution,
    calculate_release_decision,
    compute_confidence_score,
    extract_risk_level_and_score,
    summarize_test_priorities,
)


class ReleaseTestingCrew:
    """
    Main crew orchestrator with RAG-enhanced context retrieval.

    Workflow:
    1. RAG retrieves relevant bugs, stories, test cases from database
    2. Requirement Agent analyzes user story
    3. Risk Agent evaluates risks using RAG-retrieved bug history
    4. Root Cause Agent predicts likely failures
    5. Test Case Agent generates test cases
    """

    def __init__(self, user_story: str, bug_history: str):
        self.user_story = user_story
        self.bug_history = bug_history

        # RAG context populated automatically
        self.rag_context = {}

        # Agents
        self._requirement_agent = None
        self._risk_agent = None
        self._test_case_agent = None
        self._root_cause_agent = None

        # Tasks
        self._requirement_task = None
        self._risk_task = None
        self._test_task = None
        self._root_cause_task = None

        # Crew
        self._crew = None

    def _retrieve_rag_context(self) -> None:
        """Automatically retrieve relevant context from ChromaDB."""
        print("\n[+] Retrieving context from RAG database...")
        try:
            # Import lazily so Crew can run even if optional RAG dependencies are missing.
            from rag.retriever import RAGRetriever

            retriever = RAGRetriever()
            self.rag_context = retriever.get_full_context(self.user_story)
            print("   [OK] Retrieved relevant bugs from database")
            print("   [OK] Retrieved similar past user stories")
            print("   [OK] Retrieved relevant past test cases")
        except Exception as e:
            print(f"   [WARN] RAG retrieval failed: {str(e)}")
            print("   [WARN] Falling back to manually provided bug history")
            self.rag_context = {
                "relevant_bugs": self.bug_history,
                "similar_stories": "No similar stories available.",
                "relevant_test_cases": "No past test cases available."
            }

    def _build_enhanced_bug_history(self) -> str:
        """Combine RAG-retrieved bugs with manually provided bug history."""
        enhanced = ""

        if self.rag_context.get("relevant_bugs"):
            enhanced += "=== AUTO-RETRIEVED FROM DATABASE ===\n"
            enhanced += self.rag_context["relevant_bugs"]
            enhanced += "\n"

        if self.bug_history and self.bug_history.strip():
            enhanced += "=== MANUALLY PROVIDED BUG HISTORY ===\n"
            enhanced += self.bug_history
            enhanced += "\n"

        if self.rag_context.get("similar_stories"):
            enhanced += "=== SIMILAR PAST USER STORIES ===\n"
            enhanced += self.rag_context["similar_stories"]

        return enhanced

    def _create_agents(self) -> None:
        """Create all agents."""
        print("\n[+] Creating agents...")

        self._requirement_agent = create_requirement_agent()
        print("   [OK] Requirement Agent created")

        self._risk_agent = create_risk_agent()
        print("   [OK] Risk Agent created")

        self._test_case_agent = create_test_case_agent()
        print("   [OK] Test Case Agent created")

        self._root_cause_agent = create_root_cause_agent()
        print("   [OK] Root Cause Prediction Agent created")

    def _create_tasks(self) -> None:
        """Create all tasks with RAG-enhanced context."""
        print("\n[+] Creating tasks with RAG context...")

        # Build enhanced bug history combining RAG + manual
        enhanced_bug_history = self._build_enhanced_bug_history()

        # Task 1: Requirements
        self._requirement_task = create_requirement_task(
            agent=self._requirement_agent,
            user_story=self.user_story
        )
        print("   [OK] Requirement task created")

        # Task 2: Risk analysis with RAG-enhanced bug history
        self._risk_task = create_risk_task(
            agent=self._risk_agent,
            user_story=self.user_story,
            bug_history=enhanced_bug_history
        )
        print("   [OK] Risk task created with RAG-enhanced bug history")

        # Task 3: Root cause prediction with RAG-enhanced bug history
        self._root_cause_task = create_root_cause_task(
            agent=self._root_cause_agent,
            user_story=self.user_story,
            bug_history=enhanced_bug_history,
            risk_analysis="{risk_analysis}",
        )
        self._root_cause_task.context = [self._risk_task]
        print("   [OK] Root cause task created with RAG-enhanced bug history")

        # Task 4: Test cases
        self._test_task = create_test_task(
            agent=self._test_case_agent,
            requirements="{requirement_analysis}"
        )
        self._test_task.context = [self._requirement_task]
        print("   [OK] Test task created")

    def _create_crew(self) -> None:
        """Assemble the crew."""
        print("\n[+] Assembling crew...")

        self._crew = Crew(
            agents=[
                self._requirement_agent,
                self._risk_agent,
                self._root_cause_agent,
                self._test_case_agent,
            ],
            tasks=[
                self._requirement_task,
                self._risk_task,
                self._root_cause_task,
                self._test_task,
            ],
            process=Process.sequential,
            verbose=Config.VERBOSE,
        )

        print("   [OK] Crew assembled and ready")

    def run(self) -> Dict[str, Any]:
        """Execute the full pipeline with RAG context retrieval."""
        try:
            # Step 1: RAG context retrieval FIRST
            self._retrieve_rag_context()

            # Step 2: Set up and run agents
            self._create_agents()
            self._create_tasks()
            self._create_crew()

            print("\n" + "="*60)
            print("[RUNNING] EXECUTING CREW - AI Release Testing System")
            print("="*60 + "\n")

            result = self._crew.kickoff()

            print("\n" + "="*60)
            print("[DONE] CREW EXECUTION COMPLETE")
            print("="*60)

            requirements_output = self._requirement_task.output.raw if self._requirement_task.output else None
            risk_output = self._risk_task.output.raw if self._risk_task.output else None
            test_output = self._test_task.output.raw if self._test_task.output else None
            root_cause_output = self._root_cause_task.output.raw if self._root_cause_task.output else None

            # Release intelligence calculations
            risk_level, risk_numeric_score = extract_risk_level_and_score(risk_output or "")
            release_decision = calculate_release_decision(
                risk_score=risk_level,
                bug_history=self.bug_history,
                risk_analysis=risk_output or "",
            )
            confidence = compute_confidence_score(
                user_story=self.user_story,
                bug_history=self.bug_history,
                requirements=requirements_output or "",
                risk_analysis=risk_output or "",
                test_cases=test_output or "",
            )
            test_priority_summary = summarize_test_priorities(
                test_cases=test_output or "",
                bug_history=self.bug_history,
            )
            risk_distribution = build_risk_distribution(risk_level)

            return {
                "requirements": requirements_output,
                "risk_analysis": risk_output,
                "test_cases": test_output,
                "root_cause_predictions": root_cause_output,
                "raw_output": str(result),
                "risk_level": risk_level,
                "risk_numeric_score": risk_numeric_score,
                "release_decision": release_decision,
                "confidence": confidence,
                "test_priority_summary": test_priority_summary,
                "risk_distribution": risk_distribution,
                "rag_context": self.rag_context,
            }

        except Exception as e:
            print(f"\n[ERROR] Error during crew execution: {str(e)}")
            raise


def run_release_testing_crew(user_story: str, bug_history: str) -> Dict[str, Any]:
    """Convenience function to run the Release Testing Crew."""
    crew = ReleaseTestingCrew(user_story, bug_history)
    return crew.run()


def generate_root_cause_predictions(
    user_story: str,
    bug_history: str,
    risk_analysis: str,
) -> str:
    """Generate standalone root cause predictions using the RCA agent."""
    rca_agent = create_root_cause_agent()
    rca_task = create_root_cause_task(
        agent=rca_agent,
        user_story=user_story,
        bug_history=bug_history,
        risk_analysis=risk_analysis,
    )
    rca_crew = Crew(
        agents=[rca_agent],
        tasks=[rca_task],
        process=Process.sequential,
        verbose=Config.VERBOSE,
    )
    result = rca_crew.kickoff()
    return rca_task.output.raw if rca_task.output else str(result)