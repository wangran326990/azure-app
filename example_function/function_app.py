import azure.functions as func
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
key_vault_url = "https://GRAPH-APIKEY.vault.azure.net"
client_key_secret_name="Client-ID"
client_secret_secret_name="Client-Secret"
@app.route(route="email_getter")
def email_getter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    #environemnt variable example
    client_id = os.environ.get("CLIENT_ID")
    logging.info(f"Client_id: {client_id}")

    #key-vault example
    logging.info(f"Python processed Key Vault Example.")
    credential: DefaultAzureCredential = DefaultAzureCredential()
    secret_client: SecretClient = SecretClient(credential=credential,vault_url=key_vault_url)
    client_key = secret_client.get_secret(client_key_secret_name)
    logging.info(f"client_key: {client_key}")
    client_secret = secret_client.get_secret(client_secret_secret_name)
    logging.info(f"client_secret: {client_secret}")
    #end
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )