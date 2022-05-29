#!/usr/bin/env python
import stat
import pika
import os


def check_solution(id, solution_url, checker_script):
    os.mkdir(f'./tmp_solution_{id}')
    os.chdir(f'./tmp_solution_{id}')
    os.system(f'git clone {solution_url}')
    _, _, filenames = next(os.walk('.'))
    assert len(filenames) == 1
    d = filenames[0]

    os.chdir(f'./{d}')
    with open('check_solution.sh', 'w') as f:
        f.write(checker_script)
    st = os.stat('check_solution.sh')
    os.chmod('check_solution.sh', mode=st.st_mode | stat.S_IEXEC)
    result = os.popen('./check_solution.sh').read()
    return result



def on_request(ch, method, props, body):
    solution_url, checker_script = body.split('\\')
    id = props.correlation_id
    response = check_solution(id, solution_url, checker_script)

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
