from confluent_kafka import Consumer, Producer
import json

# Configuraciones iniciales
TOPIC_INPUT = "operations"  # Cambia según tu configuración
TOPIC_OUTPUT = "results"    # Cambia según tu configuración
KAFKA_BROKER = "localhost:9092"  # Cambia si usas un entorno remoto
GROUP_ID = "remotetypes_group"  # Consumer Group para evitar duplicación

# Inicializa el consumidor
consumer_config = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest'  # Configura el consumo desde el inicio
}
consumer = Consumer(consumer_config)
consumer.subscribe([TOPIC_INPUT])

# Inicializa el productor
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def process_message(message):
    """Procesa un mensaje JSON y devuelve la respuesta en el formato esperado."""
    try:
        print(f"Mensaje recibido (crudo): {repr(message)}")  # Agregado para depuración
        message = message.strip()  # Elimina espacios o saltos de línea
        operations = json.loads(message)
        responses = []

        for op in operations:
            try:
                # Validar claves obligatorias
                for key in ["id", "object_identifier", "object_type", "operation"]:
                    if key not in op:
                        raise ValueError(f"Falta la clave obligatoria: {key}")

                # Extraer información
                op_id = op["id"]
                obj_id = op["object_identifier"]
                obj_type = op["object_type"]
                operation = op["operation"]
                args = op.get("args", {})

                # Rechazar operación iter explícitamente
                if operation == "iter":
                    responses.append({
                        "id": op_id,
                        "status": "error",
                        "error": "OperationNotSupported"
                    })
                    continue

                # Simular la ejecución de la operación
                result = f"Operación {operation} ejecutada en {obj_type}:{obj_id}"  # Simulación

                # Agregar respuesta exitosa
                responses.append({
                    "id": op_id,
                    "status": "ok",
                    "result": result
                })
            except Exception as e:
                # Manejar errores
                responses.append({
                    "id": op.get("id", "unknown"),
                    "status": "error",
                    "error": type(e).__name__
                })

        return responses
    except json.JSONDecodeError as e:
        print(f"Error: Mensaje JSON malformado. Detalle: {e}")
        return []

def consume_and_process():
    """Bucle principal para consumir mensajes y procesarlos."""
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error en Kafka: {msg.error()}")
                break

        try:
            # Procesar mensaje recibido
            responses = process_message(msg.value().decode('utf-8'))

            # Enviar respuestas al topic de salida
            for response in responses:
                producer_message = json.dumps(response).encode('utf-8')
                print(f"Produciendo mensaje: {producer_message}")  # Depuración
                producer.produce(
                    TOPIC_OUTPUT,
                    value=producer_message
                )
            producer.flush()

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

if __name__ == "__main__":
    try:
        consume_and_process()
    except KeyboardInterrupt:
        print("Interrupción del usuario. Cerrando cliente.")
    finally:
        consumer.close()
        producer.flush()
