import os
import csv
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

LEADS_CSV = os.getenv("LEADS_CSV", "data/leads.csv")

def load_leads() -> List[Dict]:
    """
    Load all lead records from the CSV file.
    Returns a list of dicts, each representing one row.
    """
    if not os.path.exists(LEADS_CSV):
        return []
    with open(LEADS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_leads(leads: List[Dict]):
    """
    Overwrite the CSV file with the provided lead records.
    """
    if not leads:
        return
    os.makedirs(os.path.dirname(LEADS_CSV), exist_ok=True)
    with open(LEADS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)