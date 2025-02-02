# -*- coding: utf-8 -*-
import re
import uuid
import time
import math
import hashlib
import asyncio
import aiohttp
from pathlib import Path
from typing import List
from src.concurrency import concurrency_exec
from src.utils import PathHelper, singleton
from src.utils import TranslationConfig


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
            source = [i for i in source if
                      not re.match(r"^\s*\d+\s*(.\w+)$", i.name)]

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
            "strict": "true",
            "appKey": self.app_key
        }

    def clearSession(self):
        self.session = None

    def createSign(self, text, salt, curtime):
        text_len = len(text)
        hash256 = hashlib.sha256()
        ftext = text if text_len <= 20 else text[0:10] + str(text_len) + text[
                                                                         text_len - 10:]
        plaintext = self.app_key + ftext + salt + curtime + self.app_secret

        hash256.update(plaintext.encode("utf-8"))
        return hash256.hexdigest()

    async def exec(self, text, url, _to, _form="auto"):
        params = self.params
        async with aiohttp.ClientSession(base_url=self.base_url,
                                         headers=self.header) as session:
            response = await session.post(url, params={
                **params,
                "q": text,
                "form": _form,
                "to": _to,
                "sign": self.createSign(text, params["salt"], params["curtime"])
            })
            source = await response.json()

            if "errorCode" in source and ((code := source["errorCode"]) != "0"):
                print(f"\033[0;31m有道API出现异常，错误代码{code}\033[0m\n",
                      end="")

            if response.ok:
                if "translation" in source and len(
                    (translation := source["translation"])) > 0:
                    return translation[0]
        return text


class TranslationRecord:
    def __init__(self):
        pass


async def task(path, text):
    tconfig = TranslationConfig()
    settingConf = tconfig.settingConf

    URL, URL_PATH, APP_KEY, APP_SECRET, FROM, TO = tconfig.translationConf.values()
    thttp = TranslationHttps(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        base_url=URL
    )

    translation = await thttp.exec(text, URL_PATH, TO, FROM)

    if settingConf.get("SPECIFICATION", True):
        translation = PathHelper.fmPathName(
            translation, settingConf.get("SPACER_CHARACTER", " ")
        )
    print("结果是", translation)
    try:
        # 目录替换
        path.replace(path.parent / translation)
    except OSError:
        print("目录重命名失败", path)


def execute():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    tconfig = TranslationConfig()
    settingConf = tconfig.settingConf
    concurrencyConf = tconfig.concurrencyConf
    tdir = TranslationDir(settingConf.get("DEEP", True))
    concurrency_exec(
        task,
        list(tdir.dirs(settingConf.get("TARGET", "all"))),
        max_thread=concurrencyConf.get("MAX_THREAD", 2),
        max_coroutine=concurrencyConf.get("MAX_COROUTINE", 5),
        delay=concurrencyConf.get("DELAY", 0)
    )
    print("\033[0;32m等待结束中...\033[0m")
