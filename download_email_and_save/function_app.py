import logging
import os
import azure.functions as func
from utils.graph_api_util import GraphAPIUtil
from utils.email_dtos import MessageResponse


app = func.FunctionApp()
@app.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def get_email_timer_task(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    get_unread_emails()



def get_unread_emails():
    try:
        
        msg_resp : MessageResponse = GraphAPIUtil.get_messages_by_filter(get_email_filter())
        logging.info(f"Fetched {len(msg_resp.value)} unread emails.")
        for msg in msg_resp.value:
            logging.info(f"Email ID: {msg.id}, Subject: {msg.subject}, Received: {msg.receivedDateTime}")

            GraphAPIUtil.mark_message_as_read(msg.id)
    except Exception as e:
        logging.error(f"Error fetching unread emails: {e}")

def get_email_filter():
    # Example filter to get unread emails
    return os.getenv("EMAIL_FILTER", "isRead eq false") 