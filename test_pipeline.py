"""Phase 5: test the pipeline and validate summaries.

Run:  python test_pipeline.py
"""
import re
import time

from langchain_config import llm_chain, get_news_articles, summarize_articles

TEST_QUERIES = [
    "Tesla earnings",
    "Reliance Industries",
    "semiconductor stocks",
    "xqzvbn kjhgfdsa",  # nonsense: should return no articles without crashing
]


def numbers_in(text):
    """Extract numbers like 12, 3.5, 1,200, 8% (trailing punctuation stripped)."""
    return {n.rstrip(".,") for n in re.findall(r"\d[\d,\.]*%?", text)}


def main():
    samples, rows = {}, []
    # Task 5.1: basic functionality
    for q in TEST_QUERIES:
        t0 = time.time()
        status, n_articles, err = "", 0, ""
        try:
            articles = get_news_articles(q, page_size=10)
            src = summarize_articles(articles)
            n_articles = len(articles)
            if not src:
                status = "NO ARTICLES"
            else:
                out = llm_chain.invoke({"query": q, "summaries": src})
                samples[q] = (src, out)
                status = "PASS" if out.strip() else "EMPTY SUMMARY"
        except Exception as e:
            status, err = "ERROR", str(e)[:80]
        rows.append((q, n_articles, f"{time.time() - t0:.1f}s", status, err))

    print(f"{'Query':<28}{'Articles':>9}{'Time':>8}  Status")
    for q, n, t, s, err in rows:
        print(f"{q:<28}{n:>9}{t:>8}  {s} {err}")

    # Task 5.2: grounding check (numbers in the summary should appear in the sources)
    print("\nGrounding check:")
    for q, (src, out) in samples.items():
        nums = numbers_in(out)
        missing = sorted(n for n in nums if n not in src)
        print(f"  {q}: {len(nums)} numbers, not found in sources: {missing or 'none'}")

    assert samples, "No query passed. Check keys, model name and internet connection."
    print(f"\n{len(samples)}/{len(rows)} queries produced a summary.")


if __name__ == "__main__":
    main()
