from dataclasses import dataclass
from typing import Optional
@dataclass
class EmailAttachmentEntity:
    # Table Storage Keys
    PartitionKey: str   # Email Id
    RowKey: str         # Attachment Id

    # Email metadata
    email_subject: str
    sender: str
    receivedDateTime: str
    processDateTime: str
    attachmentName: str
    extension: str
    size: int

    # SharePoint context
    siteId: str
    siteName: str
    driveId: str
    filepath: str

    # Reporting info
    isReported: bool = False
    reportDateTime: Optional[str] = None