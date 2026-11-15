"""LangChain + Groq + NewsAPI logic for the Equity Research News Tool (Phase 4)."""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests

load_dotenv()  # reads GROQ_API_KEY and NEWSAPI_KEY from .env

# ---- LLM (Groq) -----------------------------------------------------------
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    temperature=0.2,
)

# ---- News source (NewsAPI) ------------------------------------------------
_news_key = os.getenv("NEWSAPI_KEY")
if not _news_key:
    raise RuntimeError("NEWSAPI_KEY is missing. Add it to the .env file.")


def get_news_articles(query, page_size=10, sort_by="relevancy", from_date=None):
    """Fetch English articles for a query (calls the NewsAPI HTTP endpoint directly).

    NewsAPI can return few or no articles when a small pageSize is requested,
    so we always request the maximum (100), drop unusable articles, and trim
    the list to page_size here.

    sort_by: 'relevancy', 'publishedAt' or 'popularity'.
    from_date: optional 'YYYY-MM-DD' string (oldest allowed article date).
    """
    params = {
        "q": query,
        "language": "en",
        "sortBy": sort_by,
        "pageSize": 100,
        "apiKey": _news_key,
    }
    if from_date:
        params["from"] = from_date
    resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=30)
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {data.get('code')} - {data.get('message')}")

    usable = [
        a for a in data.get("articles", [])
        if a.get("title") and a["title"] != "[Removed]" and a.get("description")
    ]
    return usable[:page_size]


def summarize_articles(articles):
    """Turn a list of article dicts into one text block for the LLM.

    Articles with no description are skipped. Each line keeps title, source,
    date and URL so the final summary can be checked against its sources.
    """
    lines = []
    for a in articles:
        if not a.get("description"):
            continue
        source = (a.get("source") or {}).get("name", "unknown source")
        date = (a.get("publishedAt") or "")[:10]
        lines.append(f"- {a.get('title')} ({source}, {date}): {a['description']} [{a.get('url')}]")
    return "\n".join(lines)


def get_summary(query, **kwargs):
    """Fetch articles for the query and return them as a formatted text block."""
    return summarize_articles(get_news_articles(query, **kwargs))


# ---- Prompt + chain -------------------------------------------------------
template = """
You are an AI assistant helping an equity research analyst. Given
the following query and the provided news article summaries, provide
an overall summary. Use ONLY the information in the articles. Cover key
themes, overall sentiment, and notable risks or catalysts. If the articles
do not cover the query, say so clearly.

Query: {query}
Summaries: {summaries}
"""
prompt = PromptTemplate(template=template, input_variables=["query", "summaries"])
llm_chain = prompt | llm | StrOutputParser()
