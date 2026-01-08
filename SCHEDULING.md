# Scheduling & Automation Guide

This guide explains how to automate the daily stock data download script (`daily_download.py`) using various methods.

## Option 1: GitHub Actions (Recommended for Cloud)

This repository includes a pre-configured GitHub Actions workflow (`.github/workflows/daily_stock_update.yml`).

*   **How it works:** GitHub's servers run the script automatically.
*   **Schedule:** Configured to run at **22:00 UTC** (market close) every weekday (Mon-Fri).
*   **Setup:**
    1.  Push this code to a GitHub repository.
    2.  Enable "Actions" in the repository settings if not already enabled.
    3.  The workflow will automatically run on schedule.
*   **Output:** The script commits the generated CSV files back to the `stock_data/` folder in your repository.

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
