"""Equity Research News Tool: final Streamlit app.

Features: optional password login (APP_PASSWORD), sidebar settings, tabs,
source list, export to .txt/.md, and query history with simple analysis.
"""
import hmac
import os
from collections import Counter
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain_config import llm_chain, get_news_articles, summarize_articles
from history import save_query, load_history, clear_history

st.set_page_config(page_title="Equity Research News Tool", page_icon="📈", layout="wide")



# ---------------- UI ----------------
st.title("📈 Equity Research News Tool")
st.caption("Fetches the latest news with NewsAPI and summarizes it with a Groq-hosted LLM.")

with st.sidebar:
    st.header("Settings")
    page_size = st.slider("Articles to fetch", 5, 30, 10)
    sort_by = st.selectbox("Sort by", ["relevancy", "publishedAt", "popularity"])
    days_back = st.slider("Look back (days)", 1, 30, 14)
    st.caption("Free NewsAPI plans only reach back about a month.")
    if os.getenv("APP_PASSWORD") and st.button("Log out"):
        st.session_state["authed"] = False
        st.rerun()

tab_search, tab_history = st.tabs(["🔎 Search", "🗂 History"])

# ---------------- Search tab ----------------
with tab_search:
    query = st.text_input("Query", placeholder="e.g. Tesla earnings, HDFC Bank, semiconductor stocks")

    if st.button("Get News", type="primary"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            try:
                with st.spinner("Fetching and summarizing news..."):
                    from_date = (date.today() - timedelta(days=days_back)).isoformat()
                    articles = get_news_articles(
                        query, page_size=page_size, sort_by=sort_by, from_date=from_date
                    )
                    summaries = summarize_articles(articles)
                    if not summaries:
                        st.session_state.pop("last", None)
                        st.info("No articles found for this query. Try different keywords or a longer look-back window.")
                    else:
                        response = llm_chain.invoke({"query": query, "summaries": summaries})
                        save_query(query, response, len(articles))          # Task 7.3
                        st.session_state["last"] = {
                            "query": query, "summary": response, "articles": articles,
                        }
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    last = st.session_state.get("last")
    if last:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Summary")
            st.write(last["summary"])
        with c2:
            st.metric("Articles used", len(last["articles"]))
            st.download_button("⬇ Download .txt", last["summary"],
                               file_name="summary.txt", mime="text/plain")
            st.download_button("⬇ Download .md",
                               f"# {last['query']}\n\n{last['summary']}\n",
                               file_name="summary.md", mime="text/markdown")
        with st.expander("Source articles"):
            for a in last["articles"]:
                src = (a.get("source") or {}).get("name", "")
                st.markdown(f"**[{a.get('title')}]({a.get('url')})**  \n"
                            f"{src} · {(a.get('publishedAt') or '')[:10]}")
                if a.get("description"):
                    st.write(a["description"])

# ---------------- History tab  ----------------
with tab_history:
    rows = load_history()
    if not rows:
        st.info("No saved searches yet. Run a search first.")
    else:
        st.subheader("Past searches")
        st.dataframe(pd.DataFrame(rows)[["timestamp", "query", "articles"]])

        counts = Counter(r["query"].strip().lower() for r in rows)
        st.subheader("Most searched queries")
        st.bar_chart(pd.Series(dict(counts.most_common(10)), name="searches"))

        per_day = Counter(r["timestamp"][:10] for r in rows)
        st.subheader("Searches per day")
        st.bar_chart(pd.Series(dict(sorted(per_day.items())), name="searches"))

        options = {f"{r['timestamp']}  -  {r['query']}": r for r in reversed(rows)}
        pick = st.selectbox("Open a past summary", list(options))
        st.write(options[pick]["summary"])

        if st.button("Clear history"):
            clear_history()
            st.rerun()
