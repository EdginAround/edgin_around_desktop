import heapq, threading, time

from typing import List

class Event():
    def __init__(self, moment, kwargs):
        self.moment = moment
        self.kwargs = kwargs

    def __eq__(self, other): return self.moment == other.moment
    def __lt__(self, other): return self.moment <  other.moment
    def __le__(self, other): return self.moment <= other.moment
    def __gt__(self, other): return self.moment >  other.moment
    def __ge__(self, other): return self.moment >= other.moment


class Scheduler:
    def __init__(self) -> None:
        self._queue: List[Event] = list()
        self._lock = threading.RLock()

    def enter(self, delay: float, **kwargs) -> None:
        moment = time.monotonic() + delay
        event = Event(moment, kwargs)
        with self._lock:
            heapq.heappush(self._queue, event)


class Runner:
    def __init__(self, processor) -> None:
        def target() -> None:
            scheduler = Scheduler()
            processor.start(scheduler)
            while self._event.is_set():
                with scheduler._lock:
                    if len(scheduler._queue) < 1: break
                    event = scheduler._queue[0]
                    heapq.heappop(scheduler._queue)

                time.sleep(max(event.moment - time.monotonic(), 0.0))
                processor.run(**event.kwargs)

        self._event = threading.Event()
        self._thread = threading.Thread(target=target)

    def start(self) -> None:
        self._event.set()
        self._thread.start()

    def stop(self) -> None:
        self._event.clear()
        self._thread.join()

