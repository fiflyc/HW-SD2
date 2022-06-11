#!/usr/bin/env python
import pika
import uuid


class Checker:

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None
        self.hw = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.hw.updateMark(int(body))

    def call(self, hw, solution_url):
        self.hw = hw
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=f'{solution_url}\\{hw.checker_script}'.encode()
        )
