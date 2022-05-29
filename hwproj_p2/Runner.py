#!/usr/bin/env python
import pika


def check_solution(solution_url, checker_script):
    return 10


def on_request(ch, method, props, body):
    solution_url, checker_script = body.split('\\')
    response = check_solution(solution_url, checker_script)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response).encode())
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))

    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    channel.start_consuming()
