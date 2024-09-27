import threading
import time

class Progress():
    def __init__(self, total: int = 1, progress: int = 0, msg: str = "", callback: callable = None) -> None:
        self.total = total
        self.progress = progress
        self.msg = msg
        self.exception = None
        self.failed = False
        self.callback = callback
        self._lock = threading.Lock()
        self.result = None
        self.thread: threading.Thread = None

    def increment_progress(self, by=1):
        with self._lock:
            self.progress += by
            self._call_callback_in_thread()

    def _call_callback_in_thread(self):
        if self.callback is None:
            return
        threading.Thread(self.callback, args=(self,), daemon=True).start()

    def set_progress(self, progress):
        with self._lock:
            self.progress = progress
            self._call_callback_in_thread()

    def set_total(self, total):
        with self._lock:
            self.total = total

    def set_msg(self, msg):
        with self._lock:
            self.msg = msg
    
    def fail(self, e):
        with self._lock:
            self.progress = self.total
            self.msg = str(e)
            self.exception = e
            self.failed = True

    def complete(self, result=None):
        with self._lock:
            self.result = result
            self.progress = self.total

    def check_fail(self):
        if self.failed:
            raise self.exception
        
    def sync(self):
        self.thread.join()
        self.check_fail()
        return self.result

    @property
    def completed(self):
        return not self.thread.is_alive()

    @property
    def percent(self):
        return round(100*self.progress/self.total, 3)
    

def runs_with_progress(func):
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
        thread = threading.Thread(target=progress_failure_catch_func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        progress.thread = thread
        return progress
    
    return progressed_function
