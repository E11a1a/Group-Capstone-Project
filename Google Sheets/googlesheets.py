import os

import gspread
from dotenv import load_dotenv

load_dotenv()
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")

client = gspread.service_account(filename=CREDENTIALS_PATH)

VALORANT_WORKSHEET = client.open_by_key(SPREADSHEET_KEY).worksheet("VALORANT ACCOUNTS")
VALORANT_SORTED_WORKSHEET = client.open_by_key(SPREADSHEET_KEY).worksheet("VALORANT ACCOUNTS [SORTED]")
