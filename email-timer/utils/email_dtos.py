from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json


@dataclass
class EmailAddress:
    name: str
    address: str

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "EmailAddress":
        return EmailAddress(
            name=obj.get("name", ""),
            address=obj.get("address", "")
        )


@dataclass
class Recipient:
    emailAddress: EmailAddress

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "Recipient":
        return Recipient(
            emailAddress=EmailAddress.from_dict(obj.get("emailAddress", {}))
        )


@dataclass
class Body:
    contentType: str
    content: str

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "Body":
        return Body(
            contentType=obj.get("contentType", ""),
            content=obj.get("content", "")
        )


@dataclass
class Flag:
    flagStatus: str

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "Flag":
        return Flag(
            flagStatus=obj.get("flagStatus", "")
        )


@dataclass
class Message:
    id: str
    createdDateTime: str
    lastModifiedDateTime: str
    changeKey: str
    categories: List[str]
    receivedDateTime: str
    sentDateTime: str
    hasAttachments: bool
    internetMessageId: str
    subject: str
    bodyPreview: str
    importance: str
    parentFolderId: str
    conversationId: str
    conversationIndex: str
    isDeliveryReceiptRequested: Optional[bool]
    isReadReceiptRequested: bool
    isRead: bool
    isDraft: bool
    webLink: str
    inferenceClassification: str
    body: Body
    sender: Recipient
    from_: Recipient  # "from" is reserved, so renamed
    toRecipients: List[Recipient]
    ccRecipients: List[Recipient]
    bccRecipients: List[Recipient]
    replyTo: List[Recipient]
    flag: Flag

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "Message":
        return Message(
            id=obj.get("id", ""),
            createdDateTime=obj.get("createdDateTime", ""),
            lastModifiedDateTime=obj.get("lastModifiedDateTime", ""),
            changeKey=obj.get("changeKey", ""),
            categories=obj.get("categories", []),
            receivedDateTime=obj.get("receivedDateTime", ""),
            sentDateTime=obj.get("sentDateTime", ""),
            hasAttachments=obj.get("hasAttachments", False),
            internetMessageId=obj.get("internetMessageId", ""),
            subject=obj.get("subject", ""),
            bodyPreview=obj.get("bodyPreview", ""),
            importance=obj.get("importance", ""),
            parentFolderId=obj.get("parentFolderId", ""),
            conversationId=obj.get("conversationId", ""),
            conversationIndex=obj.get("conversationIndex", ""),
            isDeliveryReceiptRequested=obj.get("isDeliveryReceiptRequested"),
            isReadReceiptRequested=obj.get("isReadReceiptRequested", False),
            isRead=obj.get("isRead", False),
            isDraft=obj.get("isDraft", False),
            webLink=obj.get("webLink", ""),
            inferenceClassification=obj.get("inferenceClassification", ""),
            body=Body.from_dict(obj.get("body", {})),
            sender=Recipient.from_dict(obj.get("sender", {})),
            from_=Recipient.from_dict(obj.get("from", {})),
            toRecipients=[Recipient.from_dict(r) for r in obj.get("toRecipients", [])],
            ccRecipients=[Recipient.from_dict(r) for r in obj.get("ccRecipients", [])],
            bccRecipients=[Recipient.from_dict(r) for r in obj.get("bccRecipients", [])],
            replyTo=[Recipient.from_dict(r) for r in obj.get("replyTo", [])],
            flag=Flag.from_dict(obj.get("flag", {}))
        )


@dataclass
class MessageResponse:
    odata_context: str
    value: List[Message]

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "MessageResponse":
        return MessageResponse(
            odata_context=obj.get("@odata.context", ""),
            value=[Message.from_dict(m) for m in obj.get("value", [])]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@odata.context": self.odata_context,
            "value": [m.__dict__ for m in self.value]
        }