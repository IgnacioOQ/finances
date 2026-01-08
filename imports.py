import os
import matplotlib
import multitasking

# Check if running in a headless environment (like GitHub Actions)
if os.environ.get('GITHUB_ACTIONS') == 'true':
    # Use non-interactive backend for plots to prevent crashes
    matplotlib.use('Agg')
    # Force single-threaded downloads to prevent race conditions/crashes in CI
    multitasking.set_max_threads(1)

import pandas as pd
import yfinance as yf
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
