from datetime import timedelta, timezone, datetime
from email.message import EmailMessage
import logging
import mimetypes
from pathlib import Path
import smtplib
from typing import List
import azure.functions as func
from utils.storage_table_entities import EmailAttachmentEntity
from utils.storage_table_util import StorageTableUtil
import pandas as pd
from dataclasses import asdict
import os
app = func.FunctionApp()

@app.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def daily_report_timer(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger daily report function executed.')
    generate_report()

def generate_report() -> str:
    table_name = os.getenv("STORAGE_TABLE_NAME")
    # Fetch all attachments processed in the last 24 hours
    attachments:List[EmailAttachmentEntity] = StorageTableUtil.get_all_attachments_processed_in_24hrs(table_name)
    if not attachments:
        logging.info("No attachments processed in the last 24 hours.")
        return "No attachments processed in the last 24 hours."
    # Convert to Excel
    excel_file_path = convert_to_excel(attachments)
    # send email with excel attachment
    send_gmail_with_attachment(excel_file_path)
    
    # Mark all as reported
    mark_attachments_as_reported(attachments, table_name)
    return "Report generated and email sent."  


def convert_to_excel(attachments: List[EmailAttachmentEntity]) -> str:
    data_dicts = [
        {k: v for k, v in asdict(entity).items() if k != "isReported" and k != "processDateTime"}
        for entity in attachments
    ]

    # Create a DataFrame
    df = pd.DataFrame(data_dicts)
    excel_file_name = os.getenv("EXCEL_FILE_NAME", "daily_report.xlsx")
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)

    # Build full destination path
    destination_path = os.path.join(temp_dir, excel_file_name)
    # Save to Excel
    df.to_excel(destination_path, index=False)
    return destination_path

def send_gmail_with_attachment(excel_file: str):
    SMTP_SERVER = "smtp.gmail.com"       # e.g., Gmail SMTP
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your Gmail address
    SENDER_PASSWORD = os.getenv("APP_PASSWORD")  # Your Gmail App Password
    TO_EMAIL = os.getenv("TO_EMAIL")  # Recipient's email address
    msg = EmailMessage()
    msg['Subject'] = "Test Email with Attachment"
    msg['From'] = SENDER_EMAIL
    msg['To'] = TO_EMAIL
    msg.set_content("Hello,\n\nThis is the daily report for processing vendors emails.\n\nRegards")
    file_path = Path(excel_file)
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"
    maintype, subtype = mime_type.split('/', 1)

    with open(excel_file, 'rb') as f:
        msg.add_attachment(f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=file_path.name)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # upgrade to secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

            logging.info("Email sent successfully!")

def mark_attachments_as_reported(attachments: List[EmailAttachmentEntity], table_name: str):
    entities = []
    for attachment in attachments:

        attachment.isReported = True
        attachment.processDateTime = datetime.now(timezone.utc)
        entities.append(attachment.__dict__)
    
    StorageTableUtil.batch_update_entity(table_name, entities)