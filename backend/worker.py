import pika, sys, json, time
from pika.exceptions import AMQPConnectionError, ChannelWrongStateError

from together import Together
from decouple import config
from pathlib import Path

from logger import logger
from extraction import store_pdf_data

if len(sys.argv) != 2:
    logger.error("Usage: python worker.py <API_KEY_NO>")
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

    @logger.catch
    def start(self):
        logger.info(f'Worker-{API_KEY_NO} started...')
        self.channel.start_consuming()

    @logger.catch
    def callback(self, ch, method, props, body):
        try:
            logger.info('Received task')
            logger.debug(f'Processing task: {body}')

            # Process PDF here
            new_file_id, total_pages = store_pdf_data(client, props.headers['user_id'], body.decode(), STATIC_DIR)
            logger.info(f'New file Id: {new_file_id}')
            response_json = json.dumps({'pdfStatus': 'Completed', 'pdfId': new_file_id, 'totalPages': total_pages, 'id': body.decode().split('.')[0]})
        except Exception as e:
            logger.exception(f'Error processing task: {e}')
            response_json = json.dumps({'error': "Exception from worker...", 'pdfStatus': 'Exception', 'totalPages': 0, 'id': body.decode().split('.')[0]})

        try:
            logger.info('Task completed')
            self.channel.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id=props.correlation_id, headers=props.headers),
                body=response_json
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info('Response sent')
        except ConnectionResetError as cre:
            logger.exception(f'Connection error: {cre}')
            # Start the worker again...
            raise
        except Exception as e:
            logger.exception(f'Error sending response: {e}')
            ch.basic_ack(delivery_tag=method.delivery_tag)

@logger.catch
def main():
    while True:
        try:
            pika_worker = PikaWorker()
            pika_worker.start()
        except (AMQPConnectionError, ConnectionResetError, ConnectionError, ChannelWrongStateError) as e:
            logger.exception(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unknown error: {str(e)}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
