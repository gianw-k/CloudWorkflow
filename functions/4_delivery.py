import json
import boto3
import random

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')
events = boto3.client('events')

def lambda_handler(event, context):
    print(f"--- INICIO DELIVERY --- ID: {event.get('id')}")
    
    pedido_id = event['id']
    
    # 1. Asignar un conductor aleatorio
    drivers = ["Juan Perez", "Maria Lopez", "Carlos Ruiz", "Ana Diaz"]
    driver_asignado = random.choice(drivers)
    
    # 2. Actualizar DynamoDB con estado y conductor
    table.update_item(
        Key={'id': pedido_id},
        UpdateExpression="SET #s = :status, driver = :d",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':status': 'DELIVERING',
            ':d': driver_asignado
        }
    )
    
    # 3. (Opcional) Enviar evento a EventBridge para notificaciones
    # Usamos try/except por si el LabRole no tiene permisos de EventBridge
    try:
        events.put_events(
            Entries=[{
                'Source': 'kfc.workflow',
                'DetailType': 'PedidoEnCamino',
                'Detail': json.dumps({'id': pedido_id, 'status': 'DELIVERING'}),
                'EventBusName': 'default'
            }]
        )
    except Exception as e:
        print(f"Nota: No se pudo enviar evento a EventBridge: {str(e)}")

    # 4. Retornar evento final
    event['status'] = 'DELIVERING'
    event['driver'] = driver_asignado
    event['message'] = f"Pedido en camino con {driver_asignado}"
    
    return event