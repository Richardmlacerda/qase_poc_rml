**Author: Richard Lacerda**

This repository contains the implementation for Scenario 1 and Scenario 2, as required in the Qase Technical Assessment.
The goal of this work is to demonstrate scripting skills, API integration, data transformation, and test case migration logic.

✅ **Scenario 1** — Copy Automated Test Results Between Projects

    Automated tests always publish results into **Project B**.
    The requirement is to automatically replicate these results into a matching Test Run in **Project A**, ensuring consistency between both projects.

    🧠 **Approach**

    Because Test Case IDs differ between Project A and B, a mapping strategy was required.
    The solution includes:

    A custom field in Project B that stores the corresponding Test Case ID in Project A.

    A Python script that:**qase_copy_results_v4.py** reading the variable QASE_API_TOKEN to use the personal TOKEN for QASE API.

    Reads all test results from a Test Run in Project B
    
    Maps each case to its counterpart in Project A
    
    Recreates the results inside the target Test Run in Project A
    
    Preserves result status, time, comment, and attachments (if any)
    
    🔧 **Execution**
    
    python qase_copy_results_v4.py --project-a PROJA --run-a 1 --project-b PROJB --run-b 1


✅ **Scenario 2**  
   cenario 2 — Convert TestRail HTML Tables into Markdown
    During TestRail → Qase migration, tables inside descriptions often lose formatting.
    The objective is to convert HTML table structures into valid Markdown tables programmatically.

    🧠 Approach

    Implemented function:

    def convert_testrail_tables_to_markdown(content: str) -> str:
    ...
  
  The conversion handles:
  <table>, <tr>, <td>

  Multi-line cells
  
  Spacing and alignment
  
  Removal of broken HTML fragments
  
  Standard Markdown formatting
  
  Example output:
  
  | Step | Expected Result |
  |------|-----------------|
  | Login | User is logged in |
  | Logout | Session ends |
  
   ** 🔧 Usage**
  
  The function runs automatically during migration and can also be tested individually.

  📁 Repository Structure
  scenario1/
     qase_copy_results_v4.py
     README.md
  scenario2/
     src/
     converter.py
     tests/
    requirements.txt
    main README.md

    
