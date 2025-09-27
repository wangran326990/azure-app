import azure.functions as func
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils.email_dtos import Message

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
@app.route(route="email_getter",methods=["POST"])
def email_getter(req: func.HttpRequest) -> func.HttpResponse:

        try:
            email: Message = Message.from_dict(req.get_json())
        except ValueError:
            return func.HttpResponse(
             "Invalid JSON in request body.",
             status_code=500
            )
        logging.info(f"Python HTTP trigger function processed a request. Email: {email.subject}, From: {email.from_.emailAddress}")

    
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
