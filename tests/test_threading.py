from threading import Thread
import time

def test_safe(logger, capsys):
    first_thread_initialized = False
    second_thread_initialized = False
    entered = False
    output = ""

    def non_safe_sink(msg):
        nonlocal entered
        nonlocal output
        assert not entered
        entered = True
        time.sleep(0.5)
        entered = False
        output += msg

    def first_thread():
        nonlocal first_thread_initialized
        first_thread_initialized = True
        time.sleep(0.01)
        assert second_thread_initialized
        logger.debug("message 1")

    def second_thread():
        nonlocal second_thread_initialized
        second_thread_initialized = True
        time.sleep(0.01)
        assert first_thread_initialized

        time.sleep(0.1)
        logger.debug("message 2")

    logger.start(non_safe_sink, format="{message}")

    threads = [Thread(target=first_thread), Thread(target=second_thread)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    out, err = capsys.readouterr()
    assert out == err == ""
    assert output == "message 1\nmessage 2\n"
