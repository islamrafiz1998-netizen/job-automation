import os
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# ========== USER CONFIGURATION ==========
JOB_TITLES = [
    "IT Asset Administrator", "IT Asset Coordinator", "IT Inventory Analyst",
    "IT Logistics Coordinator", "IT Deployment Specialist", "IT Delivery Coordinator",
    "Technical Operations Coordinator", "Service Desk Analyst", "IT Support Analyst",
    "IT Helpdesk Coordinator", "IT Operations Administrator", "IT Services Administrator",
    "IT Project Support Officer", "IT Project Coordinator", "IT Compliance Assistant"
]
LOCATION_KEYWORDS = ["London", "East London", "Central London"]
MIN_SALARY = 40000
YOUR_NAME = "Rafiz Islam"
YOUR_EMAIL = "islamrafiz1998@gmail.com"
CV_FILE_PATH = "your_cv.pdf"  # Upload this to Replit or your repo

# ========== GOOGLE SHEETS SETUP ==========
SHEET_ID = "10But6wym-JvxXy2usyF-5wLw9Q6Vlxi87pCFbat298s"
SHEET_RANGE = "Sheet1!A1:G1"  # Adjust as needed

# ========== GOOGLE API SETUP ==========
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send"
]
SERVICE_ACCOUNT_FILE = "credentials.json"  # Download from Google Cloud

# ========== COVER LETTER TEMPLATE ==========
COVER_LETTER_TEMPLATE = """
Dear {company},

I am writing to apply for the {job_title} position in {location}. With my experience in IT asset management and support, I am confident I can contribute to your team. In my current role, 
I oversee the deployment, return, and compliance processing of over 500 IT assets monthly across the EMEA region, ensuring full audit readiness and data security at every stage. 
I’ve led inventory updates that reduced asset discrepancies by 25% through bi-weekly audits and accurate system logging. 
I also coordinated a project that securely processed 12,000+ devices in five weeks—well ahead of schedule and without a single data breach.

My day-to-day work includes system updates, stock-level reporting, and support ticketing across laptops, phones, and desktop hardware—much like what’s described in your role. 
I’m highly organised, process-driven, and thrive in hybrid environments that require collaboration across departments and timely delivery of IT services.


I have attached my CV for your review. I look forward to discussing how I can help your organisation.

Best regards,
Rafiz Islam
"""

# ========== JOB SEARCH FUNCTION (Google Search Example) ==========
def search_jobs_google(job_titles, location_keywords, min_salary):
    # This is a placeholder for Google Search scraping.
    # In production, use an API or a scraping library like BeautifulSoup/Selenium.
    # For now, just return a mock job list.
    jobs = [
        {
            "title": "IT Asset Administrator",
            "company": "Example Corp",
            "location": "Central London",
            "salary": 42000,
            "apply_email": "hr@example.com",
            "url": "https://example.com/job/123"
        }
    ]
    return jobs

# ========== SEND EMAIL VIA GMAIL ==========
def send_email_gmail(service, to_email, subject, body, attachment_path=None):
    message = MIMEMultipart()
    message["to"] = to_email
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))
    # Attach CV if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            from email.mime.base import MIMEBase
            from email import encoders
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            message.attach(part)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {"raw": raw}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    return send_message

# ========== LOG TO GOOGLE SHEETS ==========
def log_to_sheet(sheet_service, job):
    values = [[
        job["title"], job["company"], job["location"], job["salary"], job["url"], time.strftime("%Y-%m-%d %H:%M"), "Applied"
    ]]
    body = {"values": values}
    sheet_service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID, range=SHEET_RANGE,
        valueInputOption="RAW", body=body
    ).execute()

# ========== MAIN WORKFLOW ==========
def main():
    # Authenticate with Google APIs
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheet_service = build("sheets", "v4", credentials=creds)
    gmail_service = build("gmail", "v1", credentials=creds)

    # Search for jobs
    jobs = search_jobs_google(JOB_TITLES, LOCATION_KEYWORDS, MIN_SALARY)
    for job in jobs:
        # Filter jobs
        if job["salary"] < MIN_SALARY or not any(loc in job["location"] for loc in LOCATION_KEYWORDS):
            continue
        # Generate cover letter
        cover_letter = COVER_LETTER_TEMPLATE.format(
            company=job["company"],
            job_title=job["title"],
            location=job["location"],
            your_name=YOUR_NAME
        )
        # Send application email
        send_email_gmail(
            gmail_service,
            job["apply_email"],
            f"Application for {job['title']} at {job['company']}",
            cover_letter,
            CV_FILE_PATH
        )
        # Log to Google Sheets
        log_to_sheet(sheet_service, job)
        print(f"Applied to {job['title']} at {job['company']}")

if __name__ == "__main__":
    main()
