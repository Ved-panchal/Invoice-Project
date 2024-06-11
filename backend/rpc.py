import pika, json, uuid
from sys import exit
from os import _exit

class RpcServer:
    def __init__(self) -> None:
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            self.task_queue = 'pdf_task_queue'
            self.channel.queue_declare(queue=self.task_queue, durable=True)
        except pika.exceptions.AMQPConnectionError as e:
            print(f'Connection error\nDetails: {e}')
            exit(1)

    def setup_channel(self, rpc_queue):
        try:
            self.channel.queue_declare(queue=rpc_queue)
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=rpc_queue, on_message_callback=self.on_request)
        except Exception as e:
            print(f'Error while setting up channel.\nDetails: {e}')
            exit(1)

    def start(self):
        try:
            self.channel.start_consuming()
        except Exception as e:
            print(f'Server consume error.\nDetails: {e}')
            exit(1)

    def on_request(self, ch, method, props, body):
        try:
            data = json.loads(body.decode())
            print(f" [x] Received request for {data}")

            # Enqueue each PDF path for processing
            for pdf_path in data['pdf_paths']:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.task_queue,
                    body=json.dumps({'user_id': data['user_id'], 'pdf_path': pdf_path, 'reply_to': props.reply_to, 'correlation_id': props.correlation_id}),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                    )
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError as jde:
            print(f'JSON decode error.\nDetails: {jde}')
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f'Error processing request.\nDetails: {e}')
            ch.basic_ack(delivery_tag=method.delivery_tag)

class RpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message: dict):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            body=json.dumps(message),  # Serialize list of paths as JSON
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            )
        )
        while self.response is None:
            self.connection.process_data_events()
        return self.response

def main():
    rpc_server = RpcServer()
    rpc_server.setup_channel('rpc_queue')

    print(" [x] Awaiting RPC requests")
    rpc_server.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            exit(0)
        except SystemExit:
            _exit(0)