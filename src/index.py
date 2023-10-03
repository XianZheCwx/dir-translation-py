# -*- coding: utf-8 -*-
import asyncio

import re
import uuid
import time
import math
import rtoml
import hashlib
import aiohttp
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from typing import List

from utils import PathHelper, singleton
from config import BASE_CONFIG_DIR


@singleton
class TranslationConfig:
    cache = None

    def __init__(self, path=None):
        self.path = path or BASE_CONFIG_DIR

    def read(self):
        if not self.cache:
            with open(self.path, "r", encoding="utf-8") as f:
                self.cache = rtoml.loads(f.read())

        return self.cache

    def clearCache(self):
        self.cache = None

    @property
    def translation(self):
        toml = self.read()
        if "translation" in toml:
            return toml["translation"]
        return {}

    @property
    def setting(self):
        toml = self.read()
        if "setting" in toml:
            return toml["setting"]
        return {}

    def exec(self):
        pass


class TranslationDir:
    userinput = None
    path = None

    def __init__(self, deep=True):
        self.deep = deep
        self.input()

    def input(self):
        self.userinput = input("请输入翻译目标路径：")
        self.path = Path(self.userinput)

    @PathHelper.isDirOrFile
    def dirs(self, _filter="all", ignore_num=True):
        if self.path is None:
            self.input()

        # source = []
        if _filter == "files":
            source = [i for i in self.path.iterdir() if i.is_file()]
        else:
            source = self.dirFlat(list(self.path.iterdir()))
            if _filter == "dirs":
                return [i for i in source if i.is_dir()]

        # 是否忽略数字名称
        if ignore_num:
            source = [i for i in source if not re.match(r"^\s*\d+\s*(.\w+)$", i.name)]

        return source

    @staticmethod
    def dirFlat(source: List[Path]) -> List[Path]:
        dirs = []

        def recursion(paths: List[Path]):
            for p in paths:
                dirs.append(p)
                if p.is_dir():
                    recursion(list(p.iterdir()))

        recursion(source)
        return dirs


@singleton
class TranslationHttps:
    session = None

    def __init__(self, app_key, app_secret, base_url=None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = base_url

    @property
    def header(self):
        return {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    @property
    def params(self):
        return {
            "salt": str(uuid.uuid4()),
            "curtime": str(math.trunc(time.time())),
            "signType": "v3",
            "appKey": self.app_key
        }

    def clearSession(self):
        self.session = None

    def createSign(self, text, salt, curtime):
        text_len = len(text)
        hash256 = hashlib.sha256()
        ftext = text if text_len <= 20 else text[0:10] + str(text_len) + text[text_len - 10:]
        plaintext = self.app_key + ftext + salt + curtime + self.app_secret

        hash256.update(plaintext.encode("utf-8"))
        return hash256.hexdigest()

    async def exec(self, text, url, _to, _form="auto"):
        params = self.params
        async with aiohttp.ClientSession(base_url=self.base_url, headers=self.header) as session:
            response = await session.post(url, params={
                **params,
                "q": text,
                "form": _form,
                "to": _to,
                "sign": self.createSign(text, params["salt"], params["curtime"])
            })
            if response.ok:
                source = await response.json()
                if "translation" in source and len((translation := source["translation"])) > 0:
                    return translation[0]
        return text


class TranslationRecord:
    def __init__(self):
        pass


async def task(path, text):
    tconfig = TranslationConfig()
    URL, URL_PATH, APP_KEY, APP_SECRET, FROM, TO = tconfig.translation.values()
    thttp = TranslationHttps(app_key=APP_KEY, app_secret=APP_SECRET, base_url=URL)
    translation = await thttp.exec(text, URL_PATH, TO, FROM)
    print("path.replace(translation)", path.replace(path.parent / translation))


def async_exce(path_range):
    async def main_task():
        tasks = [
            asyncio.create_task(task(path, path.name)) for path in path_range
        ]
        await asyncio.wait(tasks)

    asyncio.run(main_task())


def exec():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    pool = ThreadPoolExecutor(6)
    tconfig = TranslationConfig()
    DEEP, TARGET = tconfig.setting.values()
    tdir = TranslationDir(DEEP)
    paths = list(tdir.dirs(TARGET))

    for index in range(0, len(paths), 5):
        path_range = paths[index:index + 5]
        print(path_range)
        pool.submit(async_exce, path_range)

    print("\033[0;32m等待结束中...\033[0m")
    pool.shutdown()


if __name__ == "__main__":
    exec()
