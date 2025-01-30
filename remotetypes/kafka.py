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
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Error al leer el archivo de configuración '{config_path}'. Verifica el formato JSON.")
            return None
    else:
        logging.warning(f"No se encontró el archivo de configuración '{config_path}'.")
        logging.warning("Intentando usar variables de entorno...")

    config_data.setdefault("kafka_bootstrap_servers", os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    config_data.setdefault("group_id", os.environ.get("GROUP_ID", "remotetypes_group"))
    config_data.setdefault("input_topic", os.environ.get("INPUT_TOPIC", "operations"))
    config_data.setdefault("output_topic", os.environ.get("OUTPUT_TOPIC", "results"))

    return config_data

def invocar_operacion_remota(identificador_objeto, tipo_objeto, operacion, argumentos):
    """
    Lógica para realizar la operación en el servidor remoto.
    Ajusta esta parte con la lógica específica de tu aplicación.
    """
    if tipo_objeto in ["RSet", "RList", "RDict"]:
        return f"Procesado {operacion} en {identificador_objeto}"
    else:
        raise ValueError(f"Tipo de objeto desconocido: {tipo_objeto}")

def process_message(raw_message):
    """
    Procesa un mensaje JSON y devuelve un array de respuestas.
    """
    responses = []
    try:
        raw_message = raw_message.strip()
        operations = json.loads(raw_message)

        if isinstance(operations, dict):
            operations = [operations]
        
        if not isinstance(operations, list):
            raise ValueError("El mensaje raíz debe ser un array de operaciones.")
        
        for op in operations:
            try:
                for key in ["id", "object_identifier", "object_type", "operation"]:
                    if key not in op:
                        raise ValueError(f"Falta la clave obligatoria: {key}")
                
                op_id = op["id"]
                obj_id = op["object_identifier"]
                obj_type = op["object_type"]
                operation = op["operation"]
                args = op.get("args", {})

                if operation == "iter":
                    responses.append({
                        "id": op_id,
                        "status": "error",
                        "error": "OperationNotSupported"
                    })
                    continue
                
                result = invocar_operacion_remota(obj_id, obj_type, operation, args)
                
                responses.append({
                    "id": op_id,
                    "status": "ok",
                    "result": result
                })
            except Exception as e:
                error_id = op.get("id", "unknown")
                responses.append({
                    "id": error_id,
                    "status": "error",
                    "error": str(e)
                })
    except json.JSONDecodeError as e:
        logging.error(f"Error: Mensaje JSON malformado. Detalle: {e}")
        return []
    except Exception as e:
        logging.error(f"Error general procesando las operaciones: {e}")
        return []
    return responses

def main():
    config_data = load_config("config.json")
    if config_data is None:
        logging.error("No se pudo cargar la configuración. Abortando ejecución.")
        return

    kafka_broker = config_data["kafka_bootstrap_servers"]
    group_id = config_data["group_id"]
    topic_input = config_data["input_topic"]
    topic_output = config_data["output_topic"]

    consumer_config = {
        'bootstrap.servers': kafka_broker,
        'group.id': group_id,
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([topic_input])
    
    producer = Producer({'bootstrap.servers': kafka_broker})

    logging.info(f"Consumidor suscrito al topic: {topic_input}")
    logging.info(f"Productor enviará respuestas al topic: {topic_output}")

    try:
        while True:
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

            responses = process_message(raw_value)

            if responses:
                producer_message_bytes = json.dumps(responses, ensure_ascii=False).encode('utf-8')
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
