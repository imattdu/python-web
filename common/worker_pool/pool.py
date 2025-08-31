from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
from enum import Enum
from typing import List, Any, Tuple


class ExecutorType(str, Enum):
    THREAD = "thread"
    PROCESS = "process"


class WorkerPool:
    def __init__(self, workers: int, func, inputs: list, executor_type: str = ExecutorType.THREAD):
        """
        :param workers: 并发 worker 数量
        :param func: 执行的任务函数
        :param inputs: 每个任务的参数（列表）
        :param executor_type: 执行器类型: "thread" 或 "process"
        """
        self._workers = workers
        self._func = func
        self._inputs = inputs
        self._executor_type = executor_type

    def run(self) -> Tuple[List[Any], List[str]]:
        results = []
        exceptions = []

        executor_cls = ThreadPoolExecutor
        if self._executor_type == ExecutorType.PROCESS:
            executor_cls = ProcessPoolExecutor

        with executor_cls(max_workers=self._workers) as executor:
            futures = {executor.submit(self._func, item): item for item in self._inputs}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    exceptions.append(f"Task failed: {e}")

        return results, exceptions
