from azure.data.tables import TableServiceClient, TableClient, UpdateMode, TableTransactionError
from datetime import datetime, timedelta, timezone
import os
import logging

from utils.email_dtos import FileAttachment

class StorageTableUtil:
    table_service = None
    
    @classmethod
    def get_connection_string(cls)-> str:
        return  os.environ["AzureWebJobsStorage"]

    @classmethod
    def get_table_service(cls):
        if cls.table_service is None:
            
            cls.table_service = TableServiceClient.from_connection_string(cls.get_connection_string())
        return cls.table_service
    
    @classmethod
    def ensure_table_exists(cls, table_name: str):
        table_service = cls.get_table_service()
        try:
            table_service.create_table_if_not_exists(table_name=table_name)
        except Exception as e:
            raise Exception(f"Error creating or accessing table {table_name}: {str(e)}")
        
    @classmethod
    def get_table_client(cls, table_name: str)-> TableClient:
        cls.ensure_table_exists(table_name)
        table_service = cls.get_table_service()
        return table_service.get_table_client(table_name)
    
    @classmethod
    def insert_entity(cls, table_name: str, entity: dict):
        table_client = cls.get_table_client(table_name)
        try:
            table_client.create_entity(entity=entity)
        except Exception as e:
            raise Exception(f"Error inserting entity into table {table_name}: {str(e)}")
        
    @classmethod
    def get_all_attachments_processed_in_24hrs(cls, table_name: str):
        
        table_client = cls.get_table_client(table_name)
        try:
            twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            filter_query = f"processDateTime ge '{twenty_four_hours_ago.isoformat()} and isReported eq false'"
            entities = table_client.query_entities(filter=filter_query)
            return list(entities)
        except Exception as e:
            raise Exception(f"Error querying entities from table {table_name}: {str(e)}")
    
    @classmethod
    def batch_update_entity(cls, table_name: str, entities: list):
        table_client:TableClient = cls.get_table_client(table_name)
        batch_ops = [
        ("update", entity, {"mode": UpdateMode.MERGE}) for entity in entities
        ]
        try:
            responses = table_client.submit_transaction(batch_ops)
            return responses
        except TableTransactionError as e:
            # - e.message : error message
            # - e.response : HTTP response from the server
            logging.error("Batch update failed!")
            logging.error("Error message:", e.message)
            
            # The failed operation details are inside e.response
            logging.error("Failed operation HTTP status:", e.response.status_code)
            logging.error("Failed operation body:", e.response.text)

    @classmethod
    def get_entity(cls, table_name: str, partition_key: str, row_key: str) -> dict:
        table_client = cls.get_table_client(table_name)
        try:
            entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
            return entity
        except Exception as e:
            logging.error(f"Error retrieving entity from table {table_name}: {str(e)}")
            return None

    
    