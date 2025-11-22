#!/usr/bin/env python3
"""
Qase PoC – Copy automated results from Project B → Project A
Version 4 (Richard Lacerda) — final version.
- Uses /result/{project} instead of /result/{project}/{run_id}
- Filters by run_id manually (because Qase API does not return run-specific results when they are UI-generated)
- Fully compatible with your workspace
"""

import os
import time
import json
import argparse
import logging
from typing import List, Dict
import requests

# -------------------------
# CONFIG
# -------------------------

QASE_API_BASE = "https://api.qase.io/v1"
QASE_API_TOKEN = os.environ.get("QASE_API_TOKEN")
MAPPING_FIELD_ID = 1   # custom field "mapping_id"

if not QASE_API_TOKEN:
    raise SystemExit("ERROR: Please set QASE_API_TOKEN environment variable.")

HEADERS = {
    "Content-Type": "application/json",
    "Token": QASE_API_TOKEN
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# -------------------------
# HTTP helpers
# -------------------------

def api_get(url: str, params: dict = None) -> dict:
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
    return r.json()


def api_post(url: str, payload: dict) -> dict:
    r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
    return r.json()


# -------------------------
# Pagination helper
# -------------------------

def paginate(url: str) -> List[dict]:
    items = []
    page = 1
    while True:
        resp = api_get(url, params={"page": page, "limit": 100})
        result = resp.get("result", {})
        entities = None

        for key in ("entities", "items", "results", "cases"):
            if key in result:
                entities = result[key]
                break

        if not entities:
            break

        items.extend(entities)
        if len(entities) < 100:
            break
        page += 1
        time.sleep(0.05)

    return items


# -------------------------
# Qase Helpers
# -------------------------

def get_all_cases(project: str) -> List[dict]:
    url = f"{QASE_API_BASE}/case/{project}"
    return paginate(url)


def get_case(project: str, case_id: int) -> dict:
    url = f"{QASE_API_BASE}/case/{project}/{case_id}"
    return api_get(url).get("result")


def get_all_results(project: str) -> List[dict]:
    """
    Uses /result/{project}
    Returns ALL results, regardless of run.
    """
    url = f"{QASE_API_BASE}/result/{project}"
    return paginate(url)


def post_result(project: str, run_id: int, payload: dict) -> dict:
    url = f"{QASE_API_BASE}/result/{project}/{run_id}"
    return api_post(url, payload)


# -------------------------
# Mapping Helpers
# -------------------------

def extract_custom_field_value(cf_list: List[dict], field_id: int) -> str:
    for item in cf_list:
        if item.get("id") == field_id:
            return str(item.get("value")).strip()
    return None


def build_mapping(project: str) -> Dict[str, int]:
    """
    Builds correspondence mapping_value -> case_id
    i.e. "1001" -> 1
    """
    mapping = {}
    cases = get_all_cases(project)
    logging.info("Loaded %d cases for %s", len(cases), project)

    for case in cases:
        cf_list = case.get("custom_fields", [])
        mapping_value = extract_custom_field_value(cf_list, MAPPING_FIELD_ID)
        if mapping_value:
            mapping[mapping_value] = case["id"]

    return mapping


def convert_status(s):
    mapping = {
        "passed": 1,
        "failed": 5,
        "skipped": 2,
        "blocked": 3
    }
    if isinstance(s, int):
        return s
    return mapping.get(str(s).lower(), 4)


# -------------------------
# MAIN LOGIC
# -------------------------

def copy_results(project_a: str, run_a: int, project_b: str, run_b: int):
    logging.info("=== Building mapping from Project A ===")
    mapping_a = build_mapping(project_a)
    logging.info("Mapping keys found: %d", len(mapping_a))

    if not mapping_a:
        logging.error("No mapping_id found in Project A.")
        return

    logging.info("=== Fetching ALL results from Project B ===")
    all_results = get_all_results(project_b)
    logging.info("Fetched %d total results from %s", len(all_results), project_b)

    # Filter by RUN
    results_b = [r for r in all_results if r.get("run_id") == run_b]
    logging.info("Filtered %d results belonging to run %s", len(results_b), run_b)

    summary = {"copied": 0, "skipped": 0, "errors": 0}

    for res in results_b:
        case_id_b = res.get("case_id")
        status_raw = res.get("status")

        case_b = get_case(project_b, case_id_b)
        if not case_b:
            summary["errors"] += 1
            continue

        mapping_value = extract_custom_field_value(case_b.get("custom_fields", []), MAPPING_FIELD_ID)
        if not mapping_value:
            logging.info("Skipping case %s (no mapping_id)", case_id_b)
            summary["skipped"] += 1
            continue

        target_case_id = mapping_a.get(mapping_value)
        if not target_case_id:
            logging.info("No mapping in A for '%s'", mapping_value)
            summary["skipped"] += 1
            continue

        payload = {
            "case_id": target_case_id,
            "status": str(status_raw).lower(),
            "comment": f"Copied from {project_b} run {run_b}"
        }

        try:
            post_result(project_a, run_a, payload)
            logging.info("Copied %s → A:%s", mapping_value, target_case_id)
            summary["copied"] += 1
        except Exception as e:
            logging.error("POST error: %s", e)
            summary["errors"] += 1

        time.sleep(0.1)

    # summary.json
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logging.info("=== DONE ===")
    logging.info(summary)


# -------------------------
# CLI
# -------------------------

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-a", required=True)
    parser.add_argument("--run-a", required=True, type=int)
    parser.add_argument("--project-b", required=True)
    parser.add_argument("--run-b", required=True, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    copy_results(args.project_a, args.run_a, args.project_b, args.run_b)
