from threading import Event, Thread
from typing import List, Dict

from controller.internal.exception.combined_exception import CombinedException
from controller.internal.exception.demo_exception import DemoException


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

    def __init__(self, restart_callable: callable):
        self.main_func: callable = None
        self.restart_callable = restart_callable
        self.callable_groups: Dict[str, CallableGroup] = {}
        self._exit = False
        self.thread_exceptions: List[Exception] = []
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
            except DemoException as demo_exception:
                self._exit = True
            except Exception as e:
                self.thread_exceptions.append(e)
                self.restart_callable()
                if len(self.thread_exceptions) > 10:
                    return
                self.runner_loop(group_name, func)

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

        for thread in self.all_threads:
            thread.start()

        # start view on the main thread
        self.main_func()

        # join all threads
        for thread in self.all_threads:
            thread.join()

        if self.thread_exceptions:
            self._exit = True
            raise CombinedException(self.thread_exceptions)
