import math
import random
from pathlib import Path
from config import BASE_DIR
from typing import Dict, List, Union
from src.utils.confLoader import TestConfig


class MainTest:
    conf = TestConfig()

    def __init__(self):
        pass

    def generateHashSet(self) -> List[Dict[str, Union[str, List]]]:
        def _recursion(dataset, depth, _max=2, _min=None, parent=None):
            hashset, length = [], len(dataset)
            _min = _min or math.floor(length * 0.5) or 1

            if depth <= 0:
                return

            if _max >= length - _min:
                _max = length - _min

            for i in random.sample(
                dataset,
                random.randint(_min, _min + _max)
            ):
                path = (parent or "") + i + "\\"
                hashset.append({
                    "path": path,
                    "child": _recursion(dataset, depth - 1, parent=path)
                })

            return hashset

        if not self.conf.trainingConf:
            return

        if len(dataset := self.conf.trainingConf.get("SET", [])) <= 0:
            return

        return _recursion(
            dataset,
            self.conf.trainingConf.get("DEEP", 3),
            self.conf.trainingConf.get("MAX") or len(dataset) or 2
        )

    def mkdir(self, nodes: List[Dict[str, Union[str, List]]]):
        if not nodes or len(nodes) == 0:
            return

        base_dir = Path(self.conf.testConf.get("PATH"))

        if not base_dir.is_absolute():
            base_dir = BASE_DIR / base_dir

        for i in nodes:
            tpath = base_dir / i['path']

            # 子目录处理
            if not tpath.is_dir():
                print(f"\033[1;32m目录: {tpath}\033[0m;,")
                # 创建目录
                tpath.mkdir(parents=True, exist_ok=True)
            self.mkdir(i["child"])


def exec():
    task = MainTest()
    nodes = task.generateHashSet()
    task.mkdir(nodes)


if __name__ == '__main__':
    exec()
