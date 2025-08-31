import time
from datetime import datetime

from common.worker_pool.pool import WorkerPool, ExecutorType

if __name__ == '__main__':
    def task(*args):
        time.sleep(1)
        print(args, datetime.now())
        return args


    args = []
    for i in range(1, 100):
        args.append({i, i + 1, i + 2})

    pool = WorkerPool(10, task, args, ExecutorType.THREAD)
    res, err = pool.run()
    print(res, err)
