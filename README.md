# European AI Job Search Agent

🤖 A powerful AI-powered job search assistant specialized in finding AI/ML roles across Europe. This tool helps job seekers discover relevant positions based on their skills, experience, and preferences.

## 🌟 Features

- **Smart Job Search**: Find AI/ML positions across multiple job portals
- **Advanced Filtering**: Filter by location, experience level, skills, and more
- **AI-Powered Analysis**: Get insights into job requirements and company information
- **Customizable Search**: Tailor your search with various parameters
- **Visa Support**: Filter jobs that offer visa sponsorship
- **Remote Work Options**: Find remote or hybrid opportunities

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/job-search-agent.git
   cd job-search-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API keys (OpenAI, Firecrawl, etc.) to the `.env` file

## 🛠️ Usage

Run the job search agent:
```bash
python main.py
```

### Search Parameters
- **Keywords**: Comma-separated list of job-related terms (e.g., "AI,ML,LLM")
- **Locations**: Comma-separated list of locations (e.g., "Berlin,Remote,Amsterdam")
- **Experience Level**: Junior/Mid/Senior (comma-separated)
- **Skills**: Required technical skills (e.g., "Python,PyTorch,TensorFlow")
- **Salary**: Minimum expected salary (EUR)
- **Visa Sponsorship**: Filter jobs that offer visa support

## 🏗️ Project Structure

```
.
├── .env                    # Environment variables
├── main.py                # Main application entry point
├── pyproject.toml         # Project dependencies
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── firecrawl.py       # Web scraping service
    ├── models.py          # Data models
    ├── prompts.py         # AI prompts for job analysis
    └── workflow.py        # Job search workflow logic
```

## 🤖 Technologies Used

- Python 3.13+
- LangChain & LangGraph for workflow management
- OpenAI GPT-4 for AI-powered analysis
- Firecrawl for web scraping
- Pydantic for data validation



