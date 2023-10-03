# -*- coding: utf-8 -*-
import time
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor


def async_exce(tasks):
    """
    执行携程
    :param tasks:
    :return:
    """

    async def main_task():
        await asyncio.wait([
            asyncio.create_task(t()) for t in tasks
        ])

    asyncio.run(main_task())


def concurrency_exec(task, paths: List, max_thread=5, max_coroutine=5, delay=0):
    """
    执行并发
    :param delay:
    :param task: 需执行的任务体
    :param paths: 路径队列
    :param max_thread: 最大线程数
    :param max_coroutine: 每线程最大携程数
    """
    pool = ThreadPoolExecutor(max_thread)
    for index in range(0, len(paths), max_coroutine):
        task_range = paths[index:index + max_coroutine]

        pool.submit(async_exce, (lambda: task(i, i.name) for i in task_range))

        if delay > 0:
            time.sleep(delay)
    pool.shutdown()
