import pika, uuid, asyncio, threading
from web_socket.fastapi_socket import SocketConnectionManager
from typing import List

# class RemoteProcessClient(object):
#     def __init__(self, socket_manager:SocketConnectionManager):
#     # def __init__(self):
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host='localhost'))

#         self.socket_manager = socket_manager

#         self.channel = self.connection.channel()

#         self.callback_queue = 'callBackQueue'
#         self.rpc1_queue = 'rpc1_queue'
#         self.channel.queue_declare(queue=self.rpc1_queue, durable=True)
#         self.channel.queue_declare(queue=self.callback_queue, durable=True)

#         self.channel.basic_consume(
#             queue=self.callback_queue,
#             on_message_callback=self.on_response,
#             auto_ack=True)

#         self.response = {}
#         self.corr_id_name_map = {}

#     def on_response(self, ch, method, props, body):
#         self.response[props.correlation_id] = body
#         asyncio.create_task(self.socket_manager.send_message(body.decode(), props.headers['user_id']))
#         print("self.response: ", self.response)
#         print("self.corr_id_name_map: ", self.corr_id_name_map)

#     async def call(self, pdf_paths: List[str], user_id:str):
#         for pdf in pdf_paths:
#             self.corr_id_name_map[pdf] = str(uuid.uuid4())
#             self.channel.basic_publish(
#                 exchange='',
#                 routing_key=self.rpc1_queue,
#                 properties=pika.BasicProperties(
#                     reply_to=self.callback_queue,
#                     correlation_id=self.corr_id_name_map[pdf],
#                     headers={'user_id': user_id}
#                 ),
#                 body=pdf)
#         while len(self.response) < len(pdf_paths):
#             self.connection.process_data_events()
#         await asyncio.sleep(10)

# class RemoteProcessClient(object):
#     def __init__(self, socket_manager: SocketConnectionManager):
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host='localhost'))

#         self.socket_manager = socket_manager

#         self.channel = self.connection.channel()

#         self.callback_queue = 'callBackQueue'
#         self.rpc1_queue = 'rpc1_queue'
#         self.channel.queue_declare(queue=self.rpc1_queue, durable=True)
#         self.channel.queue_declare(queue=self.callback_queue, durable=True)

#         self.channel.basic_consume(
#             queue=self.callback_queue,
#             on_message_callback=self.on_response,
#             auto_ack=True)

#         self.responses = {}
#         self.corr_id_name_map = {}

#         # Start the event loop in a separate thread
#         self.loop = asyncio.get_event_loop()
#         if not self.loop.is_running():
#             self.loop_thread = threading.Thread(target=self.loop.run_forever)
#             self.loop_thread.start()

#     def on_response(self, ch, method, props, body):
#         print('Got response.')
#         self.responses[props.correlation_id] = body
#         future = asyncio.run_coroutine_threadsafe(
#             self.socket_manager.send_message(body.decode(), props.headers['user_id']),
#             self.loop
#         )
#         try:
#             future.result()  # Wait for the result to ensure it completed successfully
#         except Exception as e:
#             print(f"Exception in send_message: {e}")
#         print("self.responses: ", self.responses)
#         print("self.corr_id_name_map: ", self.corr_id_name_map)

#     def call(self, pdf_paths: List[str], user_id: str):
#         for pdf in pdf_paths:
#             corr_id = str(uuid.uuid4())
#             self.corr_id_name_map[pdf] = corr_id
#             self.channel.basic_publish(
#                 exchange='',
#                 routing_key=self.rpc1_queue,
#                 properties=pika.BasicProperties(
#                     reply_to=self.callback_queue,
#                     correlation_id=corr_id,
#                     headers={'user_id': user_id}
#                 ),
#                 body=pdf)
#         while len(self.responses) < len(pdf_paths):
#             self.connection.process_data_events()

import pika
import uuid
import threading
import asyncio
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

        callback_queue = 'callBackQueue_' + str(uuid.uuid4())
        channel.queue_declare(queue=callback_queue, exclusive=True)
        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        corr_id = str(uuid.uuid4())
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

        while True:
            with self.lock:
                if self.responses[corr_id] is not None:
                    response = self.responses.pop(corr_id)
                    break
            connection.process_data_events(time_limit=1)

        print(response)
        connection.close()