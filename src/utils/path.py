# -*- coding: utf-8 -*-
import re
from pathlib import Path
from functools import wraps

from src.exception import TranslationDirError


class PathHelper:

    @classmethod
    def isDirOrFile(cls, func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            if hasattr(self, "path") and isinstance(self.path, Path):
                if (not self.path.is_file()) and (not self.path.is_dir()):
                    raise TranslationDirError
            return func(self, *args, **kwargs)

        return inner

    @classmethod
    def fmPathName(cls, name: str, spacer: str, prefixes="", suffix="") -> str:
        charset = ""
        charset_arr = []
        curr_rule = None
        # 规则列表
        rules = [
            # 数字、标点符号处理
            re.compile(r"^([-_=!*/+`~@#$%^&().]|\d)$")
        ]

        for char in name:
            if char == spacer:
                continue

            if curr_rule is None:
                charset += char
                # 寻找连续类型规则
                for rule in rules:
                    if rule.match(char):
                        curr_rule = rule
            else:
                if curr_rule.match(char):
                    charset += char
                else:
                    # 重置规则
                    curr_rule = None
                    charset_arr.append(charset)
                    charset = char

        # 余量收尾
        if charset:
            charset_arr.append(charset)

        fm = spacer.join(charset_arr)
        if prefixes:
            fm = prefixes + spacer + fm
        if suffix:
            fm += spacer + suffix

        return fm
