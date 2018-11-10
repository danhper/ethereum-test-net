import logging
import signal
import time


def interruptible_infinite_loop(log_step=10, log_func=None, sleep=0):
    if log_func is None:
        log_func = lambda n: logging.info("step %s", n)
    def wrapper(f):
        def wrapped(*args, **kwargs):
            running = True

            def sigterm_handler(_sig, _frame):
                nonlocal running
                running = False

            signal.signal(signal.SIGTERM, sigterm_handler)

            n = 0
            while running:
                try:
                    f(*args, **kwargs)
                    if sleep > 0:
                        time.sleep(sleep)
                except KeyboardInterrupt:
                    running = False
                if log_step and n % log_step == 0:
                    log_func(n)
                if log_step:
                    n = n + 1
        return wrapped
    return wrapper
