#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
import logging
import argparse
import subprocess
import re

src_path = ''
dest_path = ''
items_open = {}
to_move = []

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        item = re.search(re.escape(src_path) + r"([^/]*)", event.src_path).group(1)
        # item = event.src_path.replace(src_path + "/", "")
        if not item in items_open:
            items_open[item] = 0
        items_open[item] += 1
        logging.info(f'open - item open for {event.src_path}: {item} ({items_open[item]})')

    def on_closed(self, event):
        item = re.search(re.escape(src_path) + r"([^/]*)", event.src_path)
        # item = event.src_path.replace(src_path + "/", "")
        items_open[item] -= 1
        logging.info(f'close - item open for {event.src_path}: {item} ({items_open[item]})')

def moveItemsWhichWhereCopied():
    for path, open in items_open.items():
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
    # src_path = re.sub(r"^\.\/", "", args.src_path)
    dest_path = args.dest_path
    logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(process)d) - %(levelname)s - %(message)s')

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(args.time_to_wait)
            moveItemsWhichWhereCopied()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
