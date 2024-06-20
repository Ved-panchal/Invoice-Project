import pika, sys, json, time
from pika.exceptions import AMQPConnectionError, ChannelWrongStateError
from extraction import store_pdf_data
from together import Together
from decouple import config
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python worker.py <API_KEY_NO>")
    exit(1)

API_KEY_NO = sys.argv[1]  # Read the API key from command-line arguments

# Static folder
STATIC_DIR = Path("static")
client = Together(
    api_key=config(f"TOGETHER_API_KEY_{API_KEY_NO}")
)

class PikaWorker:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.publish_queue = 'rpc1_queue'
        self.channel.queue_declare(queue=self.publish_queue, durable=True)
        self.channel.basic_consume(queue=self.publish_queue, on_message_callback=self.callback)


    def start(self):
        print(f'Worker-{API_KEY_NO} started...')
        self.channel.start_consuming()

    def callback(self, ch, method, props, body):
        try:
            print('Received task')
            print(f'Processing task: {body}')
            print(f'Static dir: {STATIC_DIR}')

            # Process PDF here
            response = store_pdf_data(client, props.headers['user_id'], body.decode(), STATIC_DIR)
            response_json = json.dumps({'pdfStatus':'Completed', 'pdfId': response, 'id': body.decode().split('.')[0]})
        except Exception as e:
            print(f'Error processing task.\nDetails: {e}')
            response_json = json.dumps({'error': str(e),'pdfStatus':'Exception'})

        try:
            print(f'task completed')
            self.channel.basic_publish(exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id = props.correlation_id, headers=props.headers),
                body=response_json)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print('Response sent...')
        except ConnectionResetError as cre:
            print(f'Connection error.\nDetails: {cre}')
            # Start the worker again...
            raise

        except Exception as e:
            print(f'Error sending response.\nDetails: {e}')
            ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            pika_worker = PikaWorker()
            pika_worker.start()
        except (AMQPConnectionError, ConnectionResetError, ConnectionError, ChannelWrongStateError) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()