"""
AI-Agent Driven Context-Aware Release Testing System
====================================================

Main entry point for the release testing system.

This system uses a multi-agent AI approach to:
1. Extract requirements from user stories
2. Analyze risks based on historical bug data
3. Generate comprehensive test cases

Usage:
    1. Create a .env file with your OpenAI API key:
       OPENAI_API_KEY=your-api-key-here
       
    2. Install dependencies:
       pip install -r requirements.txt
       
    3. Run the system:
       python main.py

Author: AI Release Testing Team
Version: 1.0.0
"""

import sys
from typing import NoReturn

from crew_setup import run_release_testing_crew


# =============================================================================
# SAMPLE INPUT DATA
# =============================================================================

# Sample user story for testing the system
SAMPLE_USER_STORY = """
As a registered user of the e-commerce platform,
I want to be able to add products to my shopping cart
So that I can purchase multiple items in a single transaction.

Acceptance Criteria:
- User must be logged in to add items to cart
- Product page should display "Add to Cart" button
- Clicking the button adds the product with selected quantity
- Cart icon should update to show total items count
- User should see a confirmation message after adding item
- Cart should persist across browser sessions
- User can add the same product multiple times
- Maximum quantity per product is 99 units
- Out-of-stock items cannot be added to cart
- Cart should display product image, name, price, and quantity
"""

# Sample bug history for risk analysis
SAMPLE_BUG_HISTORY = """
Recent Bug History (Last 6 months):

BUG-2024-001: Cart count not updating after adding items
- Severity: High
- Module: Shopping Cart
- Root Cause: State management issue in frontend
- Resolution: Fixed Redux store subscription

BUG-2024-015: Session cart data lost on browser refresh
- Severity: Critical
- Module: Shopping Cart, Session Management
- Root Cause: LocalStorage not syncing with backend
- Resolution: Implemented proper persistence layer

BUG-2024-023: Race condition when adding same item rapidly
- Severity: Medium
- Module: Shopping Cart API
- Root Cause: No debouncing on add-to-cart API calls
- Resolution: Added request debouncing

BUG-2024-045: Price calculation error with quantity > 50
- Severity: High
- Module: Cart Calculations
- Root Cause: Integer overflow in legacy calculation code
- Resolution: Migrated to BigDecimal

BUG-2024-067: Add to cart fails silently for out-of-stock items
- Severity: Medium
- Module: Inventory Integration
- Root Cause: Missing error handling for inventory check
- Resolution: Added proper error messages

BUG-2024-089: Guest users could add items without login redirect
- Severity: High
- Module: Authentication, Shopping Cart
- Root Cause: Missing auth middleware on cart endpoints
- Resolution: Added authentication guards

Historical Defect Density:
- Shopping Cart Module: 12 bugs/release (High)
- Session Management: 4 bugs/release (Medium)
- Authentication: 3 bugs/release (Low-Medium)
- Inventory Integration: 6 bugs/release (Medium)
"""


# =============================================================================
# OUTPUT FORMATTING FUNCTIONS
# =============================================================================

def print_header() -> None:
    """Print the application header."""
    print("\n" + "="*70)
    print("   AI-AGENT DRIVEN CONTEXT-AWARE RELEASE TESTING SYSTEM")
    print("="*70)
    print("\nThis system uses multiple AI agents to analyze user stories,")
    print("assess risks, and generate comprehensive test cases.\n")


def print_section(title: str, content: str) -> None:
    """
    Print a formatted section with title and content.
    
    Args:
        title: Section title to display
        content: Content to display in the section
    """
    print("\n" + "="*70)
    print(f"[*] {title}")
    print("="*70)
    print(content)
    print()


def print_input_summary(user_story: str, bug_history: str) -> None:
    """
    Print a summary of the input data.
    
    Args:
        user_story: The user story being analyzed
        bug_history: The bug history being considered
    """
    print("\n" + "-"*70)
    print("INPUT SUMMARY")
    print("-"*70)
    print("\n[USER STORY]:")
    print(user_story[:200] + "..." if len(user_story) > 200 else user_story)
    print("\n[BUG HISTORY]:")
    bug_summary = f"  - {len(bug_history.split('BUG-'))-1} historical bugs provided"
    print(bug_summary)
    print("-"*70 + "\n")


def print_results(results: dict) -> None:
    """
    Print the analysis results in a formatted manner.
    
    Args:
        results: Dictionary containing all analysis results
    """
    # Print requirements analysis
    if results.get("requirements"):
        print_section("REQUIREMENTS ANALYSIS", results["requirements"])
    
    # Print risk analysis
    if results.get("risk_analysis"):
        print_section("RISK ANALYSIS", results["risk_analysis"])
    
    # Print generated test cases
    if results.get("test_cases"):
        print_section("GENERATED TEST CASES", results["test_cases"])


def print_footer() -> None:
    """Print the application footer."""
    print("\n" + "="*70)
    print("   ANALYSIS COMPLETE")
    print("="*70)
    print("\nThe AI agents have completed their analysis.")
    print("Review the generated test cases and risk assessment above.")
    print("\n" + "="*70 + "\n")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main() -> None:
    """
    Main entry point for the Release Testing System.
    
    This function:
    1. Displays the application header
    2. Shows input summary
    3. Runs the multi-agent crew
    4. Displays formatted results
    """
    # Print application header
    print_header()
    
    # Show what we're analyzing
    print_input_summary(SAMPLE_USER_STORY, SAMPLE_BUG_HISTORY)
    
    try:
        # Run the release testing crew with sample data
        results = run_release_testing_crew(
            user_story=SAMPLE_USER_STORY,
            bug_history=SAMPLE_BUG_HISTORY
        )
        
        # Print the formatted results
        print_results(results)
        
        # Print footer
        print_footer()
        
    except ValueError as e:
        # Handle configuration errors (e.g., missing API key)
        print(f"\n[ERROR] Configuration Error: {str(e)}")
        print("\nPlease ensure you have:")
        print("  1. Created a .env file in the project directory")
        print("  2. Added your Groq API key: GROQ_API_KEY=your-key-here")
        sys.exit(1)
        
    except Exception as e:
        # Handle unexpected errors
        print(f"\n[ERROR] Unexpected Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your internet connection")
        print("  2. Your Groq API key is valid")
        print("  3. You have sufficient API credits")
        sys.exit(1)


if __name__ == "__main__":
    main()
