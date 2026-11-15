# Equity Research News Tool

A Streamlit app that fetches recent news with **NewsAPI** and summarizes it for an equity research analyst
using a **Groq**-hosted LLM through **LangChain**.

## How it works
1. The user enters a query (a company, sector or topic).
2. `langchain_config.get_news_articles` fetches matching articles from NewsAPI (direct HTTP call).
3. `summarize_articles` formats title, source, date, description and link for each article.
4. A LangChain chain (`prompt | ChatGroq | StrOutputParser`) writes an overall summary using only those articles.
5. Streamlit shows the summary, the source articles, download buttons and a search history.

## Project structure
```
news_research_tool/
├── app.py               # Streamlit interface (login, sidebar settings, tabs, history, export)
├── langchain_config.py  # NewsAPI + Groq + prompt/chain
├── history.py           # saves and loads past queries (queries_history.csv)
├── test_pipeline.py     # Phase 5 tests and summary validation
├── requirements.txt
├── README.md
├── .env                 # your keys (NOT committed)
└── .gitignore
```

## Setup
1. Python 3.9 or newer is recommended. Create and activate a virtual environment.
2. `pip install -r requirements.txt`
3. Create a `.env` file in this folder:
   ```
   GROQ_API_KEY=your-groq-key
   NEWSAPI_KEY=your-newsapi-key
   GROQ_MODEL=openai/gpt-oss-20b   
   
   ```
4. Run: `streamlit run app.py`

## Usage
- Type a query and press **Get News**.
- Use the sidebar to change the number of articles, sort order and look-back window.
- Download the summary as `.txt` or `.md`.
- The **History** tab lists past queries, shows the most searched ones and lets you reopen old summaries.

## Design notes
- **Groq model:** the model must be enabled for your key. List the models your key can use with
  `GET https://api.groq.com/openai/v1/models` (header `Authorization: Bearer <key>`) and set `GROQ_MODEL` in `.env`.
  `llama-3.3-70b-versatile` returned "model not found" for this key, so `openai/gpt-oss-20b` is the default.
- **NewsAPI:** the `newsapi-python` wrapper returned empty lists in testing, and small `pageSize` values returned few
  or no articles. The code therefore calls the HTTP API directly, requests 100 articles, filters out removed or
  description-less ones, and keeps the first `page_size`.

## Limitations
- NewsAPI free plan: limited requests per day, delayed articles, and short descriptions instead of full text.
- Summaries are only as good as the article descriptions. Always check the listed sources.
- Not financial advice.

## Running in VS Code
1. Install the **Python** extension (and **Jupyter** if you want notebooks).
2. `File > Open Folder...` and choose this `news_research_tool` folder.
3. Open a terminal (`Terminal > New Terminal`) and create a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Press `Ctrl+Shift+P` > **Python: Select Interpreter** > pick the `.venv` one.
5. `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and paste your keys into it.
7. Test the pipeline: `python test_pipeline.py`
8. Start the app: `streamlit run app.py` (opens http://localhost:8501)
