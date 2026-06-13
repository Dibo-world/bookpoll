import pika
import json
import os

def publish_vote_event(vote_data: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host)
    )
    channel = connection.channel()
    channel.queue_declare(queue="vote_events", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="vote_events",
        body=json.dumps(vote_data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    print(f"[vote-service] 메시지 발행: {vote_data}")