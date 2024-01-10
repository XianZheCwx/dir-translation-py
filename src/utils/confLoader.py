import rtoml
from pathlib import Path
from src.utils.helper import singleton
from typing import Dict, Any
from config import BASE_CONFIG_DIR, BASE_DEV_CONFIG_DIR, TEST_CONFIG_DIR


@singleton
class TranslationConfig:
    _cache = None

    def __init__(self, path=None):
        print(
            "获取配置文件路径",
            BASE_DEV_CONFIG_DIR,
            Path(BASE_DEV_CONFIG_DIR).is_file()
        )
        if path:
            self.path = path
        elif Path(BASE_DEV_CONFIG_DIR).is_file():
            print("走的是开发文件")
            self.path = BASE_DEV_CONFIG_DIR
        else:
            self.path = BASE_CONFIG_DIR

    @property
    def config(self):
        if not self._cache:
            with open(self.path, "r", encoding="utf-8") as f:
                self._cache = rtoml.loads(f.read())
        return self._cache

    def clear_cache(self):
        self._cache = None

    @property
    def translationConf(self) -> Dict[str, Any]:
        if conf := self.config["translation"]:
            return conf
        return {}

    @property
    def settingConf(self) -> Dict[str, Any]:
        if conf := self.config["setting"]:
            return conf
        return {}

    @property
    def concurrencyConf(self) -> Dict[str, Any]:
        if conf := self.config["concurrency"]:
            return conf
        return {}


@singleton
class TestConfig:
    _cache = None

    @property
    def config(self):
        if not self._cache:
            with open(TEST_CONFIG_DIR, "r", encoding="utf-8") as f:
                self._cache = rtoml.loads(f.read())
        return self._cache

    @property
    def testConf(self) -> Dict[str, Any]:
        if conf := self.config["test"]:
            return conf
        return {}

    @property
    def trainingConf(self) -> Dict[str, Any]:
        if conf := self.config["training"]:
            return conf
        return {}
