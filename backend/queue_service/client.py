import pika, uuid, asyncio, threading, json
from web_socket.fastapi_socket import SocketConnectionManager
from typing import List
from concurrent.futures import ThreadPoolExecutor

class RemoteProcessClient(object):

    def __init__(self, socket_manager: SocketConnectionManager):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.socket_manager = socket_manager
        self.callback_queue = 'callBackQueue'
        self.rpc1_queue = 'rpc1_queue'
        self.channel.queue_declare(queue=self.rpc1_queue, durable=True)
        self.channel.queue_declare(queue=self.callback_queue, durable=True)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        self.responses = {}
        self.corr_id_name_map = {}
        self.executor = ThreadPoolExecutor()
        self.lock = threading.Lock()

    def on_response(self, ch, method, props, body):
        print('Got response.')
        self.responses[props.correlation_id] = body.decode()
        self.executor.submit(asyncio.run, self.socket_manager.send_message(body.decode(), props.headers['user_id']))
        print("self.response: ", self.responses)
        print(f'body: {body}')

    def call(self, pdf_paths, user_id):
        threads = []
        for pdf in pdf_paths:
            thread = threading.Thread(target=self._send_request, args=(pdf, user_id))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def _send_request(self, pdf, user_id):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        corr_id = str(uuid.uuid4())
        callback_queue = 'callBackQueue_' + corr_id
        channel.queue_declare(queue=callback_queue, exclusive=True)
        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        self.corr_id_name_map[pdf] = corr_id
        with self.lock:
            self.responses[corr_id] = None
        channel.basic_publish(
            exchange='',
            routing_key='rpc1_queue',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
                headers={'user_id': user_id}
            ),
            body=pdf)

        # socket -> change pdf status to processing
        # self.socket_manager.send_message(pdf, user_id)
        # self.executor.submit(asyncio.run, self.socket_manager.send_message(pdf, user_id))

        while True:
            with self.lock:
                if self.responses[corr_id] is not None:
                    response = self.responses.pop(corr_id)
                    break
            connection.process_data_events(time_limit=1)

        print(response)
        connection.close()