# -*- coding: utf-8 -*-

def singleton(cls):
    """
    单例类装饰器
    :param cls:
    :return: 类实例
    """
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
