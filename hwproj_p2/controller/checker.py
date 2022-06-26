#!/usr/bin/env python
import asyncio

from aio_pika import connect_robust
from aio_pika.patterns import RPC

from hwproj_p2.model import HW


class Checker:
    """
    A class doing a remote homework check call
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.rpc = None

    @staticmethod
    async def create_checker():
        """
        Factory method
        :return: Checker
        """
        checker = Checker()
        return await checker.__connect()

    async def __connect(self):
        """
        Creates a communication channel for RPC calls
        :return: Checker
        """
        self.connection = await connect_robust(
            'amqp://guest:guest@localhost/',
            loop=asyncio.get_event_loop()
        )
        self.channel = await self.connection.channel()
        self.rpc = await RPC.create(self.channel)

        return self

    async def call(self, hw: HW, solution_url: str, on_result):
        """
        Starts checking the homework
        :param hw: HW object with homework
        :param solution_url: url to solution
        :param on_result: callback after receive result
        :return:
        """
        await on_result(
            hw.id,
            await self.rpc.proxy.check_solution(
                solution_url=solution_url,
                checker_script=hw.script
            )
        )
