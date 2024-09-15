import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': '10.8.0.2', 'port': 6002, 'scheme': 'http'}])
index_name = 'file_changes'

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

class FileChangeHandler(FileSystemEventHandler):
    def process(self, event):

        log_entry = {
            'event_type': event.event_type,
            'src_path': event.src_path,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

        if event.event_type == 'modified':
            try:
                with open(event.src_path, 'r') as file:
                    log_entry['content'] = file.read()
            except Exception as e:
                log_entry['error'] = str(e)

        es.index(index=index_name, document=log_entry)

    def on_modified(self, event):
        if not event.is_directory:
            self.process(event)

    def on_created(self, event):
        if not event.is_directory:
            self.process(event)

    def on_deleted(self, event):
        if not event.is_directory:
            self.process(event)

    def on_moved(self, event):
        if not event.is_directory:
            self.process(event)

if __name__ == "__main__":
    directory_to_watch = '/home/kali/Desktop/Workspace/'
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
