import logging
import os
import azure.functions as func
from utils.graph_api_util import GraphAPIUtil
from utils.email_dtos import MessageResponse, Message
import requests

app = func.FunctionApp()
@app.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def get_email_timer_task(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    get_unread_emails_and_process()



def get_unread_emails_and_process():
    try:
        
        msg_resp : MessageResponse = GraphAPIUtil.get_messages_by_filter(get_email_filter())
        logging.info(f"Fetched {len(msg_resp.value)} unread emails.")
        for msg in msg_resp.value:
            logging.info(f"Email ID: {msg.id}, Subject: {msg.subject}, Received: {msg.receivedDateTime}")
            #GraphAPIUtil.mark_message_as_read(msg.id)
            call_azure_email_processing_function(msg)
    except Exception as e:
        logging.error(f"Error fetching unread emails: {e}")

def get_email_filter():
    # Example filter to get unread emails
    return os.getenv("EMAIL_FILTER", "isRead eq false")

def call_azure_email_processing_function(email: Message)-> bool:
    # Placeholder for calling another Azure Function for email processing
    function_url = os.getenv("EMAIL_PROCESSING_FUNCTION_URL")
    if not function_url:
        logging.error("EMAIL_PROCESSING_FUNCTION_URL is not set.")
        return False
    try:
        response = requests.post(function_url, json=email.to_dict())
        if response.status_code == 200:
            logging.info(f"Successfully called email processing function for email ID: {email.id}")
            return True
        else:
            logging.error(f"Failed to call email processing function. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Exception while calling email processing function: {e}")
    
    return False