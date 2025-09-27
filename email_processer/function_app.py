from ast import List
import azure.functions as func
import logging
import os
from utils.email_dtos import FileAttachment, Message
from utils.graph_api_util import GraphAPIUtil
from utils.storage_table_util import StorageTableUtil
from datetime import datetime
from utils.storage_table_entities import EmailAttachmentEntity

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="email_processer")
def email_processer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    #GraphAPIUtil.upload_attachment_to_one_drive(file_path="TEST.TXT", folder_path="Attachments")

    try:
        email: Message = Message.from_dict(req.get_json())
        process_email(email)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body.",
            status_code=500
        )
    logging.info(f"Python HTTP trigger function processed a request. Email: {email.subject}, From: {email.from_.emailAddress}")

    #TODO: PROCESS EMAIL FUNCTION HERE 
    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
    )

def process_email(email: Message):
    # Example function to demonstrate processing the email
    logging.info(f"Processing email with subject: {email.subject}")
    # Add your email processing logic here

    # 1. get attachments metadata
    attachements: List[FileAttachment] = GraphAPIUtil.get_attachments_metadata(email.id)
    for attachment in attachements:
        logging.info(f"Attachment: {attachment.name}, Size: {attachment.size} bytes")
        if check_attachment_processed(email.id, attachment.id):
            logging.info(f"Attachment {attachment.name} already processed, skipping.")
            continue
    # 2. Download attachment
        destination_path: str =  GraphAPIUtil.download_attachment(attachment=attachment)
        logging.info(f"Attachment {attachment.name} downloaded to {destination_path}")
        
    # 3. Save attachment to SharePoint
        #GraphAPIUtil.upload_attachment_to_sharepoint(site_name=os.getenv("SHAREPOINT_SITE_NAME"), file_path=destination_path, folder_path="Shared Documents/General")
        GraphAPIUtil.upload_attachment_to_one_drive(file_path=destination_path, folder_path="Attachments")
        logging.info(f"Attachment {attachment.name} uploaded to OneDrive in Attachments folder.")
    # 4. Log metadata to Azure Table Storage
        entity = EmailAttachmentEntity(
            PartitionKey=email.id,
            RowKey=attachment.id,
            email_subject=email.subject,
            sender=email.from_.emailAddress.address,
            receivedDateTime=email.receivedDateTime,
            processDateTime=datetime.utcnow().isoformat(),
            attachmentName=attachment.name,
            extension=os.path.splitext(attachment.name)[1],
            size=attachment.size,
            #siteId=GraphAPIUtil.get_sharepoint_site_id(os.getenv("SHAREPOINT_SITE_NAME")),   # You can fill these fields as needed
            siteId="test",
            siteName=os.getenv("SHAREPOINT_SITE_NAME"),
            #driveId=GraphAPIUtil.get_sharepoint_drive_id(GraphAPIUtil.get_sharepoint_site_id(os.getenv("SHAREPOINT_SITE_NAME"))),
            driveId="test",
            filepath=f"/Attachments/{attachment.name}",
            isReported=False,
            reportDateTime=None
        ).__dict__
        StorageTableUtil.insert_entity(table_name=os.getenv("STORAGE_TABLE_NAME"), entity=entity)



def check_attachment_processed(email_id: str, attachment_id: str) -> bool:

    entity = StorageTableUtil.get_entity(table_name=os.getenv("STORAGE_TABLE_NAME"), partition_key=email_id, row_key=attachment_id)
   
    return entity is not None
