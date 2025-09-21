import os
import msal
import requests
import logging

from utils.email_dtos import MessageResponse
class GraphAPIUtil:
    @staticmethod
    def get_graph_api_url():
        return os.getenv("GRAPH_API_URL", "https://graph.microsoft.com/v1.0")
    
    @staticmethod
    def get_graph_api_messages_url():
        return os.getenv("GRAPH_API_MESSAGE_URL", f"{GraphAPIUtil.get_graph_api_url()}/me/messages")
         

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
        

    

    

