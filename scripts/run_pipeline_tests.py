"""
Legacy AI Platform — Bulk Pipeline Test Script

Sends a set of end-to-end test queries to the running API and logs every
request/response pair to logs/pipeline_test.log.

Usage:
    python scripts/run_pipeline_tests.py [--url http://localhost:8001]

The server must be running before you execute this script:
    uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

import urllib.request
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "http://localhost:8001"
ASK_ENDPOINT = "/api/v1/ask"
DEFAULT_USER_ID = "test_user"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pipeline_test.log")

# ── Test scenarios ─────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "label": "Early career lessons",
        "query": "What did you learn from your early career?",
    },
    {
        "label": "Mistakes and regrets",
        "query": "Tell me about a mistake you made and what you learned from it.",
    },
    {
        "label": "Parenting advice -- discipline",
        "query": "What advice would you give your son about discipline?",
    },
    {
        "label": "Person lookup -- Mike",
        "query": "Who is Mike and what is your relationship with him?",
    },
    {
        "label": "Most important life lesson",
        "query": "What is your most important life lesson?",
    },
    {
        "label": "Family relationships",
        "query": "Tell me about your relationship with your family.",
    },
    {
        "label": "Lessons from failure",
        "query": "What did you learn from your biggest failure?",
    },
    {
        "label": "Early life description",
        "query": "Describe your early life and childhood.",
    },
    {
        "label": "Relationship advice",
        "query": "What advice do you have about maintaining strong relationships?",
    },
    {
        "label": "Core values",
        "query": "What values were most important to you throughout your life?",
    },
    {
        "label": "Career regrets",
        "query": "Is there anything in your career you would have done differently?",
    },
    {
        "label": "Advice to younger self",
        "query": "What would you tell your younger self if you could?",
    },
    {
        "label": "Proudest achievement",
        "query": "What are you most proud of in your life?",
    },
    {
        "label": "Handling adversity",
        "query": "How did you handle difficult times and adversity?",
    },
    {
        "label": "Legacy and impact",
        "query": "How do you want to be remembered by your family?",
    },
]

# ── Logging setup ──────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("pipeline_tests")
    logger.setLevel(logging.DEBUG)

    # File handler — full detail
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(message)s"))

    # Console handler — progress summary (force UTF-8 on stdout)
    stdout_utf8 = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)
    ch = logging.StreamHandler(stdout_utf8)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ── HTTP helper ────────────────────────────────────────────────────────────────

def _post_ask(base_url: str, query: str, user_id: str) -> tuple[int, dict]:
    """
    POST to /api/v1/ask using only the standard library (no requests dependency).
    Returns (status_code, response_body_dict).
    """
    url = base_url.rstrip("/") + ASK_ENDPOINT
    payload = json.dumps({"query": query, "user_id": user_id}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {"detail": str(exc)}
        return exc.code, body
    except urllib.error.URLError as exc:
        return 0, {"error": str(exc.reason)}


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_tests(base_url: str, user_id: str, logger: logging.Logger) -> None:
    sep = "-" * 60
    total = len(TEST_CASES)
    passed = 0
    failed = 0

    logger.info("\n%s", sep)
    logger.info("Legacy AI Platform -- Pipeline Test Run")
    logger.info("Base URL : %s", base_url)
    logger.info("User ID  : %s", user_id)
    logger.info("Cases    : %d", total)
    logger.info("Started  : %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("%s\n", sep)

    for idx, case in enumerate(TEST_CASES, start=1):
        label = case["label"]
        query = case["query"]
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("[%d/%d] %s", idx, total, label)

        status, body = _post_ask(base_url, query, user_id)

        if status == 200:
            passed += 1
            status_label = "OK"
        elif status == 0:
            failed += 1
            status_label = "CONNECTION ERROR"
        else:
            failed += 1
            status_label = f"HTTP {status}"

        # Pretty-print body for log file
        try:
            body_text = json.dumps(body, indent=2, ensure_ascii=False)
        except Exception:
            body_text = str(body)

        # Build MEMORIES USED block (id + title from memory_details when available)
        memory_details = body.get("memory_details") or []
        memory_ids_only = body.get("memories_used") or []
        if memory_details:
            memories_block = "MEMORIES USED:\n" + "\n".join(
                f'  * {m.get("id", "?")}: "{m.get("title", "untitled")}"'
                for m in memory_details
            )
        elif memory_ids_only:
            memories_block = "MEMORIES USED:\n" + "\n".join(
                f"  * {mid}" for mid in memory_ids_only
            )
        else:
            memories_block = "MEMORIES USED: NONE"

        answer_text = body.get("answer", "") if status == 200 else (
            body.get("detail") or body.get("error") or body_text
        )

        # Log file entry — detailed with memory trace
        log_entry = (
            f"\n[{ts}]\n"
            f"CASE    : {label}\n"
            f"QUESTION: {query}\n"
            f"STATUS  : {status} {status_label}\n"
            f"{memories_block}\n"
            f"RESPONSE: {answer_text}\n"
            f"{sep}\n"
        )
        # Write directly to file handler (bypasses console handler's level filter)
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.stream.write(log_entry)
                handler.stream.flush()

        # Console — brief summary
        if status == 200:
            answer_preview = str(answer_text)[:120].replace("\n", " ")
            mem_count = len(memory_details) or len(memory_ids_only)
            logger.info("  -> %s | memories:%d | %.120s", status_label, mem_count, answer_preview)
        else:
            error_detail = body.get("error") or body.get("detail") or body_text[:200]
            logger.info("  -> %s | %s", status_label, error_detail)

    # Summary
    logger.info("\n%s", sep)
    logger.info("Results  : %d passed, %d failed out of %d", passed, failed, total)
    logger.info("Log file : %s", os.path.abspath(LOG_FILE))
    logger.info("%s\n", sep)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run bulk pipeline tests against the Legacy AI API."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the running API (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--user-id",
        default=DEFAULT_USER_ID,
        help=f"user_id sent with each request (default: {DEFAULT_USER_ID})",
    )
    args = parser.parse_args()

    logger = _setup_logging()
    run_tests(base_url=args.url, user_id=args.user_id, logger=logger)


if __name__ == "__main__":
    main()
