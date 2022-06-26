#!/usr/bin/env python
import asyncio

from aio_pika import connect_robust
from aio_pika.patterns import RPC


class Checker:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.rpc = None

    async def connect(self):
        self.connection = await connect_robust(
            'amqp://guest:guest@localhost/',
            loop=asyncio.get_event_loop()
        )
        self.channel = await self.connection.channel()
        self.rpc = await RPC.create(self.channel)

        return self

    async def call(self, hw, solution_url, on_result):
        await on_result(
            hw.id,
            await self.rpc.proxy.check_solution(
                solution_url=solution_url,
                checker_script=hw.script
            )
        )
