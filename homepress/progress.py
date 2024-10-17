import threading
import time
from typing import Any


class Progress:
    """
    A live progress tracker for live progress functions. If a function returns this object
    then you may use it to get progress updates!

    Arguments:
        total: int = 1 - The total parts of the progress based process
        progress: int = 0 - Initial progress
        msg: str = Initial message to show/display/save for the progress
        callback: callable = A callback to run in a separate thread everytime progress is set or changed

    If you are provided a progress object, ur general flow would be as follows

    ```python3
    progress = progressed_function(...)

    while not progress.completed:
        progress.check_fail()  # Check for errors
        print("Progress:", progress.percent, "%", progress.msg)
    ```

    you can also synchronise a progress to main thread using

    ```python3
    progress.sync()
    ```
    """

    def __init__(
        self,
        total: int = 1,
        progress: int = 0,
        msg: str = "",
        callback: callable = None,
        callback_threading: bool = False,
    ) -> None:
        self.total = total
        self.progress = progress
        self.msg = msg
        self.exception = None
        self.failed = False
        self.callback = callback
        self.callback_threading = callback_threading
        self._lock = threading.Lock()
        self.result = None
        self.thread: threading.Thread = None

    def increment_progress(self, by: int = 1) -> None:
        """
        Function Method

        Increments the progress by a set amount `by, which defaults to 1
        """
        with self._lock:
            self.progress += by
            self._call_callback()

    def _call_callback(self) -> None:
        if self.callback is None:
            return
        if self.callback_threading:
            threading.Thread(self.callback, args=(self,), daemon=True).start()
        else:
            self.callback(self)

    def set_progress(self, progress: int) -> None:
        """
        Function Method

        Sets the progress to given `progress`
        """
        with self._lock:
            self.progress = progress
            self._call_callback()

    def set_total(self, total: int) -> None:
        """
        Function Method

        Sets the total/completed progress
        """
        with self._lock:
            self.total = total

    def set_msg(self, msg: str) -> None:
        """
        Function Method

        Sets the Progress.msg property!
        """
        with self._lock:
            self.msg = msg

    def fail(self, e: Exception) -> None:
        """
        Function Method (Not to be used, errors raised are automatically handled by decorator)
        """
        with self._lock:
            self.progress = self.total
            self.msg = str(e)
            self.exception = e
            self.failed = True

    def complete(self, result: Any = None) -> None:
        """
        Function Method (Not to be used, return values are automatically handled by decorator)
        """
        with self._lock:
            self.result = result
            self.progress = self.total

    def check_fail(self) -> None:
        """
        Check if the function failed, if it failed, then raise the associated error
        that is saved in self.exception
        """
        if self.failed:
            raise self.exception

    def sync(self) -> Any:
        """
        Synchronise the underlying function to the main thread. Blocks until the underlying
        function has finished completion
        """
        self.thread.join()
        self.check_fail()
        return self.result

    def sync_with_progress_bar(self, poll_delay: float = 0.1) -> Any:
        """
        Synchronise the underlying function to the main thread while also displaying the
        progress to the standard output. Blocks until the underlying function has finished
        completion. A default poll_delay, updates between status update is set to 0.1 seconds
        """
        previous_msg_len = 0  # To pad extra characters
        condition = True
        while condition:
            self.check_fail()

            condition = not self.completed

            t = f"{self.progress}/{self.total} {self.percent}% {self.msg}"
            print("\r" + t.ljust(previous_msg_len), end="", flush=True)
            previous_msg_len = len(t)

            time.sleep(poll_delay)
        print()
        return self.sync()

    @property
    def completed(self) -> bool:
        """
        Check if the progress has completed or if its still alive
        """
        return not self.thread.is_alive()

    @property
    def percent(self) -> float:
        """
        Get the percentage value for the current progress as a float rounded off to 3 decimals
        """
        return round(100 * self.progress / self.total, 3)


def runs_with_progress(func: callable) -> callable:
    """
    A decorator to convert a function to run with progress
    The function should take a "progress" keyword argument of type `Progress`

    The function then may proceed to set the total by `progress.set_total(<total amount to do>)`
    The function may increment progress by `progress.increment_progress([<by: int = 1>])`
    The function may set an optional display message with `progress.set_msg(<msg: str>)`
    The function may set the progress by `progress.set_progress(<progress>)`

    ```python
    import time

    @runs_with_progress
    def my_function(a, b, c, progress):
        progress.set_total(3)
        progress.set_msg("Working")
        for x in (a, b, c):
            time.sleep(1)
            print(x)
            progess.increment_progress()
        progress.set_msg("Finished")

    progress = my_function(1, 2, 3)
    progress.sync()  # Or other functions from progress!
    ```
    """

    def progressed_function(*args, **kwargs):
        progress = Progress()

        def progress_failure_catch_func(*args, **kwargs):
            progress = kwargs["progress"]
            try:
                result = func(*args, **kwargs)
                progress.complete(result)
            except Exception as e:
                progress.fail(e)

        kwargs["progress"] = progress
        thread = threading.Thread(
            target=progress_failure_catch_func, args=args, kwargs=kwargs, daemon=True
        )
        thread.start()
        progress.thread = thread
        return progress

    return progressed_function
