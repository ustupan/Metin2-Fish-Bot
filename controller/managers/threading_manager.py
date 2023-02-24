from threading import Event, Thread
from typing import List, Dict


# Sometimes there are connected operations e.g. Fishing and Message Scanning,
# sometimes I want to do other stuff independently e.g. drop the unwanted fish during fishing
# also sometimes I want to stop fishing during doing other stuff
# CallableGroup groups these operations e.g. to walk and buy bait I want to pause fishing and
# start walking and buying the bait
class CallableGroup:
    def __init__(self, tasks: List[callable]):
        self.pause = Event()
        self.tasks = tasks
        self.pause.clear()

    def set_pause(self, paused):
        if paused:
            self.pause.clear()
        else:
            self.pause.set()


class ThreadingManager:

    def __init__(self):
        self.main_func: callable = None
        self.callable_groups: Dict[str, CallableGroup] = {}
        self._exit = False
        self.thread_exception: Exception = None
        self.system_pause = Event()
        self.system_pause.clear()
        self.all_threads: List[Thread] = []

    # Todo add pause on specific callable group
    def runner_loop(self, group_name: str, func: callable):
        while True:
            if self.system_pause.is_set() is False:
                self.system_pause.wait()
            if self._exit is True:
                return

            try:
                func()
            except Exception as e:
                self.thread_exception = e
                return

    @staticmethod
    def start_threads_in_group(thread_group: List[Thread]):
        for thread in thread_group:
            thread.start()

    @staticmethod
    def join_threads_in_group(thread_group: List[Thread]):
        for thread in thread_group:
            thread.join()

    def start(self):
        threads_groups: List[List[Thread]] = list()
        if bool(self.callable_groups):
            for group_name, callable_group in self.callable_groups.items():
                threads_group: List[Thread] = list()
                if callable_group.tasks:
                    for sub_task in callable_group.tasks:
                        thread = Thread(target=self.runner_loop, args=(group_name, sub_task,))
                        threads_group.append(thread)
                        self.all_threads.append(thread)
                threads_groups.append(threads_group)

        for threads_group in threads_groups:
            self.start_threads_in_group(threads_group)

        # start view on the main thread
        self.main_func()

        # join all threads
        for thread in self.all_threads:
            thread.join()

        if self.thread_exception:
            raise self.thread_exception
