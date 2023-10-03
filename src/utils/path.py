# -*- coding: utf-8 -*-
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
