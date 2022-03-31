import time
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import watchdog.events

class Watcher:

    def __init__(self, directory=".", handler=RegexMatchingEventHandler()):
        self.observer = Observer()
        self.handler = MyHandler()
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class MyHandler(watchdog.events.RegexMatchingEventHandler):

    def __init__(self):
        watchdog.events.RegexMatchingEventHandler.__init__(self, regexes=['.*/bleh$'], ignore_regexes=[], ignore_directories=False, case_sensitive=False)

    def on_created(self, event):
        print("Oh no! It's gone!")

    def on_deleted(self, event):
        print("It's back!")

if __name__=="__main__":
    w = Watcher(".", MyHandler())
    w.run()
