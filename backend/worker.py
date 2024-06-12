import pika, json, sys
from openai import OpenAI
from together import Together
from decouple import config
from pathlib import Path
from extraction import store_pdf_data

if len(sys.argv) != 2:
    print("Usage: python worker.py <API_KEY_NO>")
    exit(1)

API_KEY_NO = sys.argv[1]  # Read the API key from command-line arguments

# Static folder
STATIC_DIR = Path("static")

client = Together(
    api_key = config(f'TOGETHER_API_KEY_{API_KEY_NO}')
)

def on_task_request(ch, method, properties, body):
    try:
        task_info = json.loads(body)
        user_id = task_info['user_id']
        pdf_path = task_info['pdf_path']
        reply_to = task_info['reply_to']
        correlation_id = task_info['correlation_id']

        print(f" [x] Processing PDF {pdf_path}")

        response = store_pdf_data(client, user_id, pdf_path, STATIC_DIR)
        response_json = json.dumps({pdf_path: response})
    except Exception as e:
        print(f'Error processing task.\nDetails: {e}')
        response_json = json.dumps({'error': str(e)})

    try:
        ch.basic_publish(
            exchange='',
            routing_key=reply_to,
            body=response_json,
            properties=pika.BasicProperties(
                correlation_id=correlation_id
            )
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'Error sending response.\nDetails: {e}')
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pdf_task_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='pdf_task_queue', on_message_callback=on_task_request)

    print(' [*] Waiting for PDF processing tasks. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
