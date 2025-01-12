Requisitos del Sistema

Software Necesario
- Python 3.8
- Apache Kafka 
- Librerías de Python:
  - `confluent_kafka`
  - `Ice`

---

Instalación y Configuración

Instalar Dependencias
Asegúrate de instalar todas las dependencias necesarias ejecutando:

bash
pip install confluent-kafka zeroc-ice


Configurar Apache Kafka
primero git clone el repositorio del profesor
sudo docker-compose up


---

Ejecución del Cliente

Configurar el Cliente
Abre el archivo del cliente Kafka (`kafka.py`) y asegúrate de que las siguientes variables tengan los valores correctos:

python
TOPIC_INPUT = "operations"
TOPIC_OUTPUT = "results"
KAFKA_BROKER = "localhost:9092"
GROUP_ID = "remotetypes_group"
```

Ejecutar el Cliente
Inicia el cliente Kafka con:
primero asegurarse de que el docker esta de pie con sudo docker-compose up 
python kafka.py


El cliente estará consumiendo mensajes del topic `operations` y enviará las respuestas procesadas al topic `results`.

---

Pruebas del Cliente

Enviar Mensajes al Topic de Entrada
Usa el productor Kafka para enviar mensajes al topic `operations`:
en otro terminal sudo docker exec -it kafka /bin/bash
bin/kafka-console-producer.sh --topic operations --bootstrap-server localhost:9092


Ejemplo de mensaje JSON:

json
[
  {
    "id": "1",
    "object_identifier": "test_obj",
    "object_type": "RDict",
    "operation": "setItem",
    "args": {"key": "key1", "value": "value1"}
  }
]


Ver Respuestas en el Topic de Salida
Usa el consumidor Kafka para verificar las respuestas:
bin/kafka-console-consumer.sh --topic results --from-beginning --bootstrap-server localhost:9092

