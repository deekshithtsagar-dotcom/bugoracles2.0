# AI-Agent Driven Context-Aware Release Testing System

A production-ready multi-agent AI system that automates release testing workflows using CrewAI and OpenAI's GPT-4o-mini.

## 🎯 Overview

This system leverages three specialized AI agents to:

1. **Requirement Agent** - Extracts functional requirements, edge cases, negative cases, and test scenarios from user stories
2. **Risk Agent** - Analyzes risks based on user stories and historical bug data
3. **Test Case Agent** - Generates comprehensive, structured test cases

## 📁 Project Structure

```
ai_release_testing/
│
├── agents/
│   ├── __init__.py              # Agents module exports
│   ├── requirement_agent.py      # Requirement extraction agent
│   ├── risk_agent.py            # Risk analysis agent
│   └── test_case_agent.py       # Test case generation agent
│
├── tasks/
│   ├── __init__.py              # Tasks module exports
│   ├── requirement_task.py      # Requirement extraction task
│   ├── risk_task.py             # Risk analysis task
│   └── test_task.py             # Test case generation task
│
├── crew_setup.py                # CrewAI orchestration setup
├── config.py                    # Configuration and LLM initialization
├── main.py                      # Main entry point with sample data
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- OpenAI API key

### 2. Installation

```bash
# Clone or navigate to the project directory
cd ai_release_testing

# Create and activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-actual-api-key-here
```

### 4. Run the System

```bash
python main.py
```

## 📋 Sample Output

The system produces three main outputs:

### Requirements Analysis
- Functional Requirements (FR-001, FR-002, ...)
- Edge Cases (EC-001, EC-002, ...)
- Negative Cases (NC-001, NC-002, ...)
- Test Scenarios (TS-001, TS-002, ...)

### Risk Analysis
- Risk Score: LOW / MEDIUM / HIGH
- Risk Explanation with key factors
- Suggested Testing Depth

### Test Cases
Each test case includes:
- Test Case ID (TC-001, TC-002, ...)
- Title
- Preconditions
- Steps
- Expected Result
- Priority (HIGH / MEDIUM / LOW)

## ⚙️ Configuration Options

Edit `config.py` to customize:

```python
class Config:
    MODEL_NAME = "gpt-4o-mini"  # OpenAI model to use
    TEMPERATURE = 0.3          # Lower = more deterministic
    VERBOSE = True             # Enable detailed logging
    MAX_ITERATIONS = 5         # Max agent iterations
```

## 🔧 Customization

### Using Your Own User Story

Edit `main.py` and modify `SAMPLE_USER_STORY`:

```python
SAMPLE_USER_STORY = """
As a [user type],
I want to [action]
So that [benefit].

Acceptance Criteria:
- Criterion 1
- Criterion 2
"""
```

### Adding Bug History

Edit `main.py` and modify `SAMPLE_BUG_HISTORY`:

```python
SAMPLE_BUG_HISTORY = """
BUG-001: Description
- Severity: High/Medium/Low
- Module: Affected module
- Root Cause: What caused it
"""
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| crewai | >=0.86.0 | Multi-agent orchestration |
| openai | >=1.58.0 | OpenAI API client |
| python-dotenv | >=1.0.0 | Environment management |
| langchain | >=0.3.0 | LLM framework |
| pydantic | >=2.0.0 | Data validation |

## 🔐 Security

- **Never commit `.env` files** with actual API keys
- Use environment variables for sensitive data
- The `.env.example` file is safe to commit

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
- Ensure `.env` file exists in the project root
- Verify the API key is set correctly

### "Rate limit exceeded"
- Wait a few minutes before retrying
- Consider upgrading your OpenAI plan

### "Connection error"
- Check your internet connection
- Verify OpenAI API status at status.openai.com

## 📄 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with ❤️ using CrewAI and OpenAI
