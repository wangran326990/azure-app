import base64
import os
from typing import List
import msal
import requests
import logging

from utils.email_dtos import FileAttachment, MessageResponse
class GraphAPIUtil:
    @staticmethod
    def get_graph_api_url():
        return os.getenv("GRAPH_API_URL", "https://graph.microsoft.com/v1.0")
    
    @staticmethod
    def get_graph_api_messages_url():
        return os.getenv("GRAPH_API_MESSAGE_URL", f"{GraphAPIUtil.get_graph_api_url()}/me/messages")

    @staticmethod
    def get_hostname():
        return os.getenv("HOSTNAME", "")     

    @staticmethod
    def get_sharepoint_site_id(site_name: str):
        response = requests.get(
            f"{GraphAPIUtil.get_graph_api_url()}/{GraphAPIUtil.get_hostname()}:/sites/{site_name}",
            headers={
                "Authorization": f"Bearer {GraphAPIUtil.get_access_token()}",
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            site_info = response.json()
            return site_info.get("id", "")
        else:
            raise Exception(f"Error fetching SharePoint site ID: {response.status_code} {response.text}")
        
    
    @staticmethod
    def get_sharepoint_drive_id(site_id: str = None):
        response = requests.get(
            f"{GraphAPIUtil.get_graph_api_url()}/sites/{site_id}/drive",
            headers={
                "Authorization": f"Bearer {GraphAPIUtil.get_access_token()}",
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            driver_info = response.json()
            return driver_info.get("id", "")
        else:
            raise Exception(f"Error fetching Driver ID: {response.status_code} {response.text}")

    @staticmethod
    def get_tenant_id():
        return os.getenv("TENANT_ID", "")

    @staticmethod
    def get_client_id():
        return os.getenv("CLIENT_ID", "")

    @staticmethod
    def get_client_secret():
        return os.getenv("CLIENT_SECRET", "")
    
    @staticmethod
    def get_msal_app():
        return msal.ConfidentialClientApplication(
            client_id=GraphAPIUtil.get_client_id(),
            client_credential=GraphAPIUtil.get_client_secret(),
            authority=f"https://login.microsoftonline.com/{GraphAPIUtil.get_tenant_id()}"
        )
    
    @staticmethod
    def get_access_token():
        # if token provided in env, use it directly (for testing)
        token = os.getenv("TOKEN", None)
        if token:
            logging.info("Using token from environment variable.")
            return token
        app = GraphAPIUtil.get_msal_app()
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception("Could not obtain access token from MSAL.")

    @staticmethod
    def get_messages_by_filter(filter: str) -> MessageResponse:
        token = GraphAPIUtil.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"{GraphAPIUtil.get_graph_api_messages_url()}?$filter={filter}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            msg_resp : MessageResponse = MessageResponse.from_dict(response.json())
            logging.info(f"response: {response.text}")
            return msg_resp
        else:
            raise Exception(f"Error fetching messages: {response.status_code} {response.text}")
        

    @staticmethod
    def mark_message_as_read(message_id: str) -> None:
        token = GraphAPIUtil.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"{GraphAPIUtil.get_graph_api_messages_url()}/{message_id}"
        body = {
            "isRead": True
        }
        response = requests.patch(url, headers=headers, json=body)
        if response.status_code == 200:
            logging.info(f"Message {message_id} marked as read.")
        else:
            raise Exception(f"Error marking message as read: {response.status_code} {response.text}")
        
    
    @staticmethod
    def mark_message_as_unread(message_id: str) -> None:
        token = GraphAPIUtil.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"{GraphAPIUtil.get_graph_api_messages_url()}/{message_id}"
        body = {    
            "isRead": False
        }
        response = requests.patch(url, headers=headers, json=body)
        if response.status_code == 200:
            logging.info(f"Message {message_id} marked as unread.")
        else:
            raise Exception(f"Error marking message as unread: {response.status_code} {response.text}")
        
    @staticmethod
    def upload_attachment_to_sharepoint(site_name: str, file_path: str, folder_path: str) -> None:
        token = GraphAPIUtil.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        file_name = os.path.basename(file_path)
        site_id = GraphAPIUtil.get_sharepoint_site_id(site_name)
        drive_id = GraphAPIUtil.get_sharepoint_drive_id(site_id)
        url = f"{GraphAPIUtil.get_graph_api_url()}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
        with open(file_path, 'rb') as file_data:
            response = requests.put(url, headers=headers, data=file_data)
            if response.status_code in (200, 201):
                logging.info(f"File {file_name} uploaded to SharePoint folder {folder_path}.")
            else:
                raise Exception(f"Error uploading file to SharePoint: {response.status_code} {response.text}")

    @staticmethod
    def get_attachments_metadata(message_id: str)->List[FileAttachment]:
        token = GraphAPIUtil.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"{GraphAPIUtil.get_graph_api_messages_url()}/{message_id}/attachments"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            attachments_data = response.json().get("value", [])
            attachments = [FileAttachment(
                odata_type=att.get("@odata.type", ""),
                id=att.get("id", ""),
                name=att.get("name", ""),
                size=att.get("size", 0),
                media_content_type=att.get("@odata.mediaContentType", ""),
                media_read_link=att.get("@odata.mediaReadLink", ""),
                content_bytes=att.get("contentBytes", None)
            ) for att in attachments_data if att.get("@odata.type") == "#microsoft.graph.fileAttachment"]
            return attachments
        else:
            raise Exception(f"Error fetching attachments: {response.status_code} {response.text}")     

    @staticmethod
    def download_attachment(attachment: FileAttachment) -> str:
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        destination_path = os.path.join(temp_dir, attachment.name)
        if not attachment.media_read_link:
            if attachment.content_bytes:
            # Decode base64 content
                file_content = base64.b64decode(attachment.content_bytes)
                # Write to file
                with open(destination_path, "wb") as f:
                    f.write(file_content)
                    logging.info(f"Attachment saved as {destination_path}")
            else:
                raise Exception("No content available for attachment.")
        else:
            token = GraphAPIUtil.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}"
            }
            download_url = attachment.media_read_link
            response = requests.get(download_url, stream=True, headers=headers)
        
            if response.status_code == 200:
                with open(destination_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                logging.info(f"Attachment {attachment.name} downloaded to {destination_path}.")
            else:
                raise Exception(f"Error downloading attachment: {response.status_code} {response.text}")

        return destination_path  

    

    

