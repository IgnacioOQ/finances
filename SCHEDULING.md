# Scheduling & Automation Guide

This guide explains how to automate the daily stock data download script (`daily_download.py`) using various methods.

## Option 1: GitHub Actions (Recommended for Cloud)

This repository includes a pre-configured GitHub Actions workflow (`.github/workflows/daily_stock_update.yml`).

*   **How it works:** GitHub's servers run the script automatically.
*   **Schedule:** Configured to run at **22:00 UTC** (market close) every weekday (Mon-Fri).
*   **Output:** The script commits the generated CSV files back to the `stock_data/` folder in your repository.

### Troubleshooting: "I don't see the workflow"
If you cannot see "Daily Stock Update" in the Actions tab:
1.  **Check the Branch:** Workflows generally only appear in the list **after** the code has been merged to the default branch (usually `main` or `master`). If you are working on a feature branch, you may need to filter by that branch or open the specific "Push" event to see the run.
2.  **Enable Actions:** Go to **Settings > Actions > General** in your repository and ensure "Allow all actions and reusable workflows" is selected.

### Learning: How to Create the Workflow Manually
If you want to understand how to set this up yourself from scratch:

1.  Go to your GitHub repository.
2.  Click the **Actions** tab.
3.  Click **New workflow**.
4.  Click **set up a workflow yourself** (usually a link at the top).
5.  Name the file `daily_stock_update.yml`.
6.  Paste the configuration. Here is a breakdown of what the code does:

```yaml
name: Daily Stock Update

on:
  schedule:
    # "Cron" syntax: minute hour day_of_month month day_of_week
    # 22:00 UTC on Mon,Tue,Wed,Thu,Fri
    - cron: '0 22 * * 1-5'
  workflow_dispatch:  # Allows you to click "Run workflow" manually button

jobs:
  update-stocks:
    runs-on: ubuntu-latest  # The virtual machine environment

    # Permission to write to the repo (to save the CSVs)
    permissions:
      contents: write

    steps:
    # 1. Download your code
    - name: Checkout repository
      uses: actions/checkout@v3

    # 2. Install Python
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    # 3. Install libraries
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pandas yfinance matplotlib tqdm requests beautifulsoup4 lxml html5lib

    # 4. Run your script
    - name: Run daily download script
      run: python daily_download.py

    # 5. Save the results (Git Commit & Push)
    - name: Commit and push changes
      run: |
        git config --global user.name "GitHub Action"
        git config --global user.email "action@github.com"
        git add stock_data/
        git commit -m "Auto-update stock data" || echo "No changes to commit"
        git push
```

## Option 2: Local Scheduling (Mac/Linux) - `cron`

If you prefer to run this on your local machine (which must be ON at the scheduled time):

1.  Open your terminal.
2.  Type `crontab -e` to edit your cron jobs.
3.  Add the following line to run the script every weekday at 5:00 PM (17:00):
    ```bash
    0 17 * * 1-5 /usr/bin/python3 /path/to/your/repo/daily_download.py >> /path/to/your/repo/daily.log 2>&1
    ```
    *(Note: Replace `/path/to/your/repo/` with the actual full path to the file. Run `which python3` to confirm your python path.)*

## Option 3: Local Scheduling (Windows) - Task Scheduler

1.  Open **Task Scheduler**.
2.  Click **Create Basic Task**.
3.  **Name:** "Daily Stock Download".
4.  **Trigger:** Daily, at your preferred time (e.g., 5:00 PM).
5.  **Action:** Start a program.
    *   **Program/script:** `python.exe` (or full path to your python executable).
    *   **Add arguments:** `daily_download.py`
    *   **Start in:** `C:\path\to\your\repo\` (Full path to the folder containing the script).
6.  Finish.

## Option 4: Other Cloud Providers

If you need more computing power or don't want to use GitHub Actions:

*   **PythonAnywhere:**
    *   Upload your files.
    *   Go to the "Tasks" tab.
    *   Create a scheduled task to run `python daily_download.py` daily.
    *   (Free tier has limitations, paid tier allows outgoing requests to Yahoo Finance).

*   **AWS Lambda + EventBridge:**
    *   More complex setup.
    *   Requires packaging the script and dependencies (pandas, yfinance) into a Lambda layer or Docker container.
    *   Use EventBridge (CloudWatch Events) to trigger the function on a schedule.
