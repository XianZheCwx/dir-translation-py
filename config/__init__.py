# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]

CONFIG_DIR = BASE_DIR / "config"

BASE_CONFIG_DIR = CONFIG_DIR / "./index.toml"

# 开发环境下配置文件
BASE_DEV_CONFIG_DIR = CONFIG_DIR / "./dev.toml"

# 测试配置文件
TEST_CONFIG_DIR = CONFIG_DIR / "./test.toml"
