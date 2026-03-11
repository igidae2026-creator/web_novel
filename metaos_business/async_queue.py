from __future__ import annotations
from dataclasses import dataclass
from queue import Queue, Empty
from threading import Thread, Event
from typing import Callable, Any, Optional

@dataclass
class Task:
    fn: Callable[..., Any]
    args: tuple
    kwargs: dict

class AsyncQueue:
    def __init__(self, worker_count: int = 1):
        self.q: Queue[Task] = Queue()
        self.stop_event = Event()
        self.workers = [Thread(target=self._worker, daemon=True) for _ in range(max(1, int(worker_count)))]
        for w in self.workers:
            w.start()

    def submit(self, fn: Callable[..., Any], *args, **kwargs):
        self.q.put(Task(fn=fn, args=args, kwargs=kwargs))

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                task = self.q.get(timeout=0.2)
            except Empty:
                continue
            try:
                task.fn(*task.args, **task.kwargs)
            finally:
                self.q.task_done()

    def shutdown(self, wait: bool = True):
        self.stop_event.set()
        if wait:
            for w in self.workers:
                w.join(timeout=1.0)
