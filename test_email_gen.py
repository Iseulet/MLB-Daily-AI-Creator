import json
import os
import sys
from phase_1_research_automation.src.formatter import format_email

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'phase-1_research-automation', 'src'))
from formatter import format_email
    print(f"Subject: {subject}")
    print("-" * 20)
    print(body[:1000])  # Print first 1000 chars to check language

if __name__ == "__main__":
    test_email_gen()
