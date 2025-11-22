import json
import boto3
import time

# Inicializamos DynamoDB fuera del handler para reusar conexión
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')

def lambda_handler(event, context):
    print(f"--- INICIO PAGOS --- ID: {event['id']}")
    
    # 1. Simular validación de pago
    time.sleep(2)
    payment_id = "TXN-STRIPE-OK"
    
    # 2. Actualizar DynamoDB
    table.update_item(
        Key={'id': event['id']},
        UpdateExpression="SET #s = :status, paymentId = :pid",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':status': 'PAID', ':pid': payment_id}
    )
    
    # 3. Retornar datos actualizados al Step Function
    event['status'] = 'PAID'
    event['paymentId'] = payment_id
    return event