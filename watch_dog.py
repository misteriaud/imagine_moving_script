#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.observers import api
from watchdog.observers.inotify import InotifyObserver
from watchdog.events import FileSystemEventHandler
from multiprocessing import Pipe

import os
import logging
import argparse
import subprocess
import re

class CustomObserver(InotifyObserver):
    def __init__(self, conn, timeout=...):
        self.conn = conn
        super().__init__(timeout)

    def dispatch_events(self, event_queue):
        entry = event_queue.get(block=True)
        if entry is api.EventDispatcher._stop_event:
            return
        event, _ = entry

        with self._lock:
            if event.is_directory:
                return
            if event.event_type == "created" or event.event_type == "modified":
                self.conn.send(event.src_path)

        event_queue.task_done()

def moveSyscall(path, args):
    full_path = os.path.join(args.src_path, path)
    try:
        subprocess.run(['mv', full_path, args.dest_path], check = True)
        logging.info(f'move {path}')
    except:
        pass
        # logging.error(f'error: couldn\'t move {path} to {dest_path}')

def routine(conn, args):
    items = dict()
    while True:
        try:
            if conn.poll(1):
                path = conn.recv()
                regex = r"(?<=" + re.escape(args.src_path) + r")[^/]*"
                item = re.search(regex, path).group(0)
                items[item] = time.time_ns()
            to_move = []
            current_time = time.time_ns()
            for item, last_modified in items.items():
                if current_time - last_modified > args.time_to_wait * 1e9:
                    to_move.append(item)
            for item in to_move:
                del items[item]
                moveSyscall(item, args)
        except Exception:
            logging.error("Unkown error occured")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'Utilitaire de deplacement de fichier',
        description = 'Permet de deplacer tous les fichiers et dossiers présents du dossier source au dossier destination, en verifiant que les elements ne sois pas en cours de dépot.'
    )
    parser.add_argument('src_path', help='emplacement du dossier source')
    parser.add_argument('dest_path', help='emplacement du dossier destination')
    parser.add_argument('time_to_wait', help='temps d\attente en seconde entre chaque boucle', type=int)
    args = parser.parse_args()
    # logging.basicConfig(level=logging.INFO, filename="app.log", format='%(asctime)s (%(process)d) - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s\t%(message)s\t')
    if not os.path.isdir(args.src_path) or not os.path.isdir(args.dest_path):
        raise Exception("arguments arent describing directories")
    logging.info(f"start watchdog over {args.src_path}")

    parent_conn, child_conn = Pipe(duplex=False)
    observer = CustomObserver(child_conn)
    observer.schedule(FileSystemEventHandler(), path=args.src_path, recursive=True)
    observer.start()

    try:
        routine(parent_conn, args)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
