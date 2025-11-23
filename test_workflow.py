#!/usr/bin/env python3
"""
Script para probar el workflow de KFC Order Flow
"""
import boto3
import json
import time
from datetime import datetime

# Configuración
STATE_MACHINE_ARN = "arn:aws:states:us-east-1:971647339908:stateMachine:KfcOrderWorkflow"
REGION = "us-east-1"

def test_workflow():
    # Cliente de Step Functions
    sf_client = boto3.client('stepfunctions', region_name=REGION)
    
    # Cargar el pedido de prueba
    with open('pedido_test.json', 'r') as f:
        pedido = json.load(f)
    
    print("Iniciando ejecución del workflow...")
    print(f"Pedido: {pedido['id']}")
    print(f"Total: S/{pedido['total']}")
    print("-" * 50)
    
    # Iniciar ejecución
    execution_name = f"test-{int(time.time())}"
    response = sf_client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=execution_name,
        input=json.dumps(pedido)
    )
    
    execution_arn = response['executionArn']
    print(f"Ejecución iniciada: {execution_name}")
    print(f"🔗 ARN: {execution_arn}")
    print("-" * 50)
    
    # Monitorear ejecución
    print("\nMonitoreando ejecución...")
    while True:
        status = sf_client.describe_execution(executionArn=execution_arn)
        current_status = status['status']
        
        print(f"Estado: {current_status}", end='\r')
        
        if current_status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
            print(f"\n\n🏁 Ejecución finalizada: {current_status}")
            
            if current_status == 'SUCCEEDED':
                output = json.loads(status['output'])
                print("\n RESULTADO EXITOSO:")
                print(json.dumps(output, indent=2, ensure_ascii=False))
                
                # Mostrar resumen
                print("\n" + "=" * 50)
                print("RESUMEN DEL PEDIDO:")
                print("=" * 50)
                print(f"ID: {output.get('id')}")
                print(f"Pago: {output.get('paymentId')}")
                print(f"Estado Cocina: {output.get('status')}")
                print(f"Empaquetado: {'✓' if output.get('status') == 'PACKED' or output.get('status') == 'IN_DELIVERY' else '✗'}")
                print(f"Delivery: {output.get('driver', 'Sin asignar')}")
                print(f"Tiempo estimado: {output.get('estimatedTime', 'N/A')}")
                
            elif current_status == 'FAILED':
                print("\nEJECUCIÓN FALLIDA:")
                if 'error' in status:
                    print(f"Error: {status.get('error')}")
                if 'cause' in status:
                    print(f"Causa: {status.get('cause')}")
            
            break
        
        time.sleep(2)
    
    # Verificar tabla DynamoDB
    print("\n" + "=" * 50)
    print("VERIFICANDO DYNAMODB...")
    print("=" * 50)
    
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table('Orders')
    
    try:
        item = table.get_item(Key={'id': pedido['id']})
        if 'Item' in item:
            print("Pedido encontrado en DynamoDB:")
            print(json.dumps(item['Item'], indent=2, default=str, ensure_ascii=False))
        else:
            print("Pedido no encontrado en DynamoDB")
    except Exception as e:
        print(f"Error al consultar DynamoDB: {e}")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
