# -*- coding: utf-8 -*-

class TranslationDirError(Exception):
    def __init__(self, msg="翻译路径错误"):
        # super().__init__()
        self.msg = msg
        pass

    def __str__(self):
        return self.msg

