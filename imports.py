import os
import matplotlib

# Check if running in a headless environment (like GitHub Actions)
if os.environ.get('GITHUB_ACTIONS') == 'true':
    matplotlib.use('Agg')

import pandas as pd
import yfinance as yf
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
