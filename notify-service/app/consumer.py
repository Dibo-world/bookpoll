import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[notify-service] 메시지 수신: {data}")
    # 여기에 알림 로직 추가 (이메일, 로그 등)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    channel.queue_declare(queue="vote_events", durable=True)
    channel.basic_consume(queue="vote_events", on_message_callback=callback)
    print("[notify-service] 메시지 대기 중... (종료: Ctrl+C)")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()