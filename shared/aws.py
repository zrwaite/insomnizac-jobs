import boto3
from boto3.dynamodb.types import TypeDeserializer
from shared.config import env
import json

def send_sns_notification(message):
    sns = boto3.client('sns')
    try:
        res = sns.publish(
            TopicArn=env['SNS_TOPIC_ARN'],
            Message=message
        )
        print("Sent SNS notification")
        print(res)
    except Exception as e:
        print(f"Error sending SNS notification: {e}")

def get_dynamodb_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)

def dynamodb_to_python(dynamodb_response):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamodb_response.items()}

def get_db_item(id, table_name):
    table = get_dynamodb_table(table_name)
    try:
        response = table.get_item(Key={'id': id})
        parsed_response = dynamodb_to_python(response.get('Item'))
        return parsed_response
    except Exception as e:
        print(f"Error getting item from DynamoDB: {e}")
        return None

def set_db_item(item, table_name):
    table = get_dynamodb_table(table_name)
    try:
        table.put_item(Item=item)
    except Exception as e:
        print(f"Error setting item in DynamoDB: {e}")

def get_dynamodb_client():
    """Retrieve a DynamoDB client."""
    return boto3.client('dynamodb')

def chunk_list(lst, chunk_size):
    """Yield successive chunks of given list with specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def get_db_items(ids, table_name):
    client = get_dynamodb_client()
    try:
        items = []
        for batch in chunk_list(ids, 100):
            # Format keys properly depending on data type (assumes 'id' is the partition key)
            keys = [{'id': {'S': str(item_id)}} for item_id in batch]  # Use 'N' if ID is a number

            response = client.batch_get_item(
                RequestItems={
                    table_name: {
                        'Keys': keys
                    }
                }
            )
            batch_items = response.get('Responses', {}).get(table_name, [])
            for item in batch_items:
                items.append(dynamodb_to_python(item))
        return items
    except Exception as e:
        print(f"Error getting items from DynamoDB: {e}")
        return []

def set_db_items(items, table_name):
    client = get_dynamodb_client()
    try:
        for batch in chunk_list(items, 25):
            requests = []
            for item in batch:
                requests.append({
                    'PutRequest': {
                        'Item': item
                    }
                })
            response = client.batch_write_item(
                RequestItems={
                    table_name: requests
                }
            )
            print(f"Batch write response: {response}")
    except Exception as e:
        print(f"Error setting items in DynamoDB: {e}")

def default_handler(func, success_message):
    try:
        func()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': success_message,
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 