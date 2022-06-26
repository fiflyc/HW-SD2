#!/usr/bin/env python
import stat
import os
import asyncio
import uuid
from aio_pika import connect_robust
from aio_pika.patterns import RPC


def check_solution(solution_url: str, checker_script: str) -> int:
    """
    Checks the homework
    :param solution_url:
    :param checker_script:
    :return: result
    """
    id = str(uuid.uuid4())
    os.mkdir(f'./tmp_solution_{id}')
    os.chdir(f'./tmp_solution_{id}')
    os.system(f'git clone {solution_url}')
    _, folders, _ = next(os.walk('.'))
    assert len(folders) == 1, f'len(filenames) == {len(folders)}'
    d = folders[0]

    os.chdir(f'./{d}')
    with open('check_solution.sh', 'w') as f:
        f.write(checker_script)
    st = os.stat('check_solution.sh')
    os.chmod('check_solution.sh', mode=st.st_mode | stat.S_IEXEC)
    result = os.popen('./check_solution.sh').read()
    return int(result)


async def main():
    connection = await connect_robust('amqp://guest:guest@localhost/')

    channel = await connection.channel()

    rpc = await RPC.create(channel)
    await rpc.register('check_solution', check_solution, auto_delete=True)

    try:
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == '__main__':
    asyncio.run(main())
