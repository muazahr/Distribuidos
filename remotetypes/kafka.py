import os
import json
import logging
from confluent_kafka import Consumer, Producer, KafkaError

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

def load_config(config_path="config.json"):
    """
    Carga la configuración desde un archivo JSON o, en caso de no hallarlo,
    intenta usar variables de entorno como fallback.
    """
    config_data = {}
    
    # Intenta cargar desde archivo
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        logging.warning(f"No se encontró el archivo de configuración '{config_path}'.")
        logging.warning("Intentando usar variables de entorno...")

    # Variables de entorno como valores por defecto o reemplazo
    config_data.setdefault("kafka_bootstrap_servers", os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    config_data.setdefault("group_id", os.environ.get("GROUP_ID", "remotetypes_group"))
    config_data.setdefault("input_topic", os.environ.get("INPUT_TOPIC", "operations"))
    config_data.setdefault("output_topic", os.environ.get("OUTPUT_TOPIC", "results"))

    return config_data

def process_message(raw_message):
    """
    Procesa un mensaje JSON y devuelve un array de respuestas,
    de acuerdo al formato especificado.
    
    Formato de entrada (array de objetos JSON):
    [
      {
        "id": <obligatorio>,
        "object_identifier": <obligatorio>,
        "object_type": <obligatorio>,
        "operation": <obligatorio>,
        "args": <opcional>
      },
      ...
    ]
    
    Formato de salida (array de objetos JSON):
    [
      {
        "id": <string|number>,
        "status": "ok" | "error",
        "result": <opcional si ok>,
        "error": <opcional si error>
      },
      ...
    ]
    """
    responses = []
    try:
        raw_message = raw_message.strip()
        operations = json.loads(raw_message)

        # Verificar que sea un array de operaciones
        if not isinstance(operations, list):
            raise ValueError("El mensaje raíz debe ser un array de operaciones.")
        
        for op in operations:
            try:
                # Validar que existan las cuatro claves obligatorias
                for key in ["id", "object_identifier", "object_type", "operation"]:
                    if key not in op:
                        raise ValueError(f"Falta la clave obligatoria: {key}")
                
                op_id = op["id"]
                obj_id = op["object_identifier"]
                obj_type = op["object_type"]
                operation = op["operation"]
                args = op.get("args", {})

                # Manejo especial de "iter"
                if operation == "iter":
                    responses.append({
                        "id": op_id,
                        "status": "error",
                        "error": "OperationNotSupported"
                    })
                    continue
                
                # Simula el procesamiento de la operación
                result = f"Operación '{operation}' ejecutada en '{obj_type}:{obj_id}' con args={args}"

                # Respuesta exitosa
                responses.append({
                    "id": op_id,
                    "status": "ok",
                    "result": result
                })

            except Exception as e:
                # Error a nivel de operación
                error_id = op.get("id", "unknown")
                responses.append({
                    "id": error_id,
                    "status": "error",
                    "error": type(e).__name__
                })

    except json.JSONDecodeError as e:
        logging.error(f"Error: Mensaje JSON malformado. Detalle: {e}")
        # Retornar lista vacía o alguna respuesta de error genérica
        return []

    except Exception as e:
        logging.error(f"Error general procesando las operaciones: {e}")
        return []

    return responses

def main():
    # Carga de configuración
    config_data = load_config("config.json")

    kafka_broker = config_data["kafka_bootstrap_servers"]
    group_id = config_data["group_id"]
    topic_input = config_data["input_topic"]
    topic_output = config_data["output_topic"]

    # Inicializa el consumidor
    consumer_config = {
        'bootstrap.servers': kafka_broker,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'  # Cambia a 'latest' si quieres consumir solo nuevos mensajes
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([topic_input])
    
    # Inicializa el productor
    producer = Producer({'bootstrap.servers': kafka_broker})

    logging.info(f"Consumidor suscrito al topic: {topic_input}")
    logging.info(f"Productor enviará respuestas al topic: {topic_output}")

    try:
        while True:
            # Consumir mensaje
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logging.error(f"Error en Kafka: {msg.error()}")
                    break

            raw_value = msg.value().decode('utf-8')
            logging.info(f"Mensaje recibido: {raw_value}")

            # Procesar el mensaje
            responses = process_message(raw_value)

            # Publicar las respuestas (un único mensaje con un array JSON)
            if responses:
                # Usamos ensure_ascii=False para no escapar caracteres Unicode
                # y luego encodeamos para obtener bytes
                producer_message_bytes = json.dumps(responses, ensure_ascii=False).encode('utf-8')

                # Imprimimos decodificado para ver el JSON sin b'' ni escapes
                logging.info(f"Enviando respuestas: {producer_message_bytes.decode('utf-8')}")

                producer.produce(topic_output, value=producer_message_bytes)
                producer.flush()

    except KeyboardInterrupt:
        logging.warning("Interrupción del usuario (Ctrl+C). Cerrando el consumidor.")
    finally:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    main()
