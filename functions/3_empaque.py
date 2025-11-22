import json
import boto3
import time

# Inicializamos recurso fuera del handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')

def lambda_handler(event, context):
    print(f"--- INICIO EMPAQUE --- ID: {event.get('id')}")
    
    pedido_id = event['id']
    
    # 1. Simular proceso de empaquetado (2 segundos)
    time.sleep(2)
    
    # 2. Actualizar estado en DynamoDB
    try:
        table.update_item(
            Key={'id': pedido_id},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':status': 'PACKED'}
        )
    except Exception as e:
        print(f"Error actualizando DynamoDB: {str(e)}")
        # No detenemos el flujo, pero logeamos el error
    
    # 3. Retornar evento actualizado
    event['status'] = 'PACKED'
    event['message'] = "Pedido empaquetado correctamente"
    
    return event