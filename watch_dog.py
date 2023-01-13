#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.observers import api
from watchdog.observers import polling
from watchdog.events import FileSystemEventHandler

import os
import logging
import argparse
import subprocess
import re

src_path = ''
dest_path = ''
items_open = {}
# items_open = []
to_move = []

class MyHandler(FileSystemEventHandler):
    def dispatch(self, event):
        event_type = event.event_type
        path = event.src_path
        is_directory = event.is_directory
        if (event_type != "created" and event_type != "closed") or is_directory:
            return
        regex = r"(?<=" + re.escape(src_path) + r")[^/]*"
        item = re.search(regex, path).group(0)
        if not item in items_open:
            items_open[item] = 0
        if event_type == "created":
            items_open[item] += 1
        else:
            items_open[item] -= 1
        logging.info(f'{event_type} \t{item} - {items_open[item]}')

def moveItemsWhichWhereCopied():
    for path, open in items_open.items():
        logging.info(f"{path}: {open}")
        if not open:
            to_move.append(path)
    been_moved = []
    for path in to_move:
        if path not in items_open:
            been_moved.append(path)
        if items_open[path] == 0:
            moveSyscall(path)
            del items_open[path]
            been_moved.append(path)
    for moved in been_moved:
        to_move.remove(moved)

def moveSyscall(path):
    full_path = os.path.join(src_path, path)
    try:
        subprocess.run(['mv', full_path, dest_path], check = True)
        logging.info(f'move {path} to {dest_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'error: couldn\'t move {path} to {dest_path}')

# def scanEvents(event_queue):
#     while not event_queue.empty():
#         entry = event_queue.get(block=True)
#         event, _ = entry
#         event_type = event.event_type
#         path = event.src_path
#         is_directory = event.is_directory
#         if (event_type != "created" and event_type != "closed") or is_directory:
#             continue
#         regex = r"(?<=" + re.escape(src_path) + r")[^/]*"
#         item = re.search(regex, path).group(0)
#         if not item in items_open:
#             items_open[item] = 0
#         if event_type == "created":
#             items_open[item] += 1
#         else:
#             items_open[item] -= 1
#         logging.info(f'{event_type} \t{path} - {items_open[item]}')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'Utilitaire de deplacement de fichier',
        description = 'Permet de deplacer tous les fichiers et dossiers présents du dossier source au dossier destination, en verifiant que les elements ne sois pas en cours de dépot.'
    )
    parser.add_argument('src_path', help='emplacement du dossier source')
    parser.add_argument('dest_path', help='emplacement du dossier destination')
    parser.add_argument('time_to_wait', help='temps d\attente en seconde entre chaque boucle', type=int)
    args = parser.parse_args()
    src_path = args.src_path
    dest_path = args.dest_path
    logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(process)d) - %(levelname)s - %(message)s')

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(args.time_to_wait)
            # scanEvents(observer.event_queue)
            # moveItemsWhichWhereCopied()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
