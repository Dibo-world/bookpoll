import pika
import json

def publish_vote_event(vote_data: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
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

# publish_vote_event({
#     "event": "vote_created",
#     "book_id": vote.book_id,
#     "user_id": vote.user_id
# })