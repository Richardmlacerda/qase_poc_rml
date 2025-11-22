Qase API – Result Sync PoC (Scenario 1)

This repository contains a small Proof-of-Concept script developed for the Qase Solutions & Implementation Engineer assessment.

The goal of the PoC is simple:
Copy automated test results from a run in Project B into the corresponding run in Project A, matching the correct test cases using a custom field (mapping_id).

🚀 What the script does

Reads test cases from Project A

Builds a mapping using the custom field mapping_id

Fetches all test results from Project B

Filters only results from the selected run

Posts the mapped results into the selected run in Project A

I built this in Python even though I'm not a developer by trade, focusing on clarity, correctness, and understanding of Qase’s API behavior.

🧩 API Detail Discovered

During testing, I found that:

GET /result/{project}/{run_id}


does not return UI-generated results.
To ensure full compatibility, the script uses:

GET /result/{project}


and filters by run_id.

This is something real customers could encounter, so I adapted the solution accordingly.

▶ Running the PoC
pip install requests
export QASE_API_TOKEN="your_token"
python qase_copy_results_v4.py --project-a PROJA --run-a 1 --project-b PROJB --run-b 1

✔ Status

Tested successfully:

3 cases mapped

3 results copied

0 errors

The script aims to be simple, understandable, and practical, reflecting how I solve real implementation problems.