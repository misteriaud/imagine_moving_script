import os
import time
import shutil
import logging
import argparse
import subprocess

def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                try:
                    total += get_directory_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total

def move_to(path, new_path):
    try:
        stat = os.stat(path)
        subprocess.run(['mv', path, new_path], check = True)
        # new_path = shutil.move(path, new_path)
        # shutil.chown(new_path, user=stat.st_uid, group=stat.st_gid)
        # os.chmod(new_path, 750)
        logging.info(f'move {path} to {new_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'error: couldn\'t move {path} to {new_path}')

def main():
    parser = argparse.ArgumentParser(
        prog = 'Utilitaire de deplacement de fichier',
        description = 'Permet de deplacer tous les fichiers et dossiers présents du dossier source au dossier destination, en verifiant que les elements ne sois pas en cours de dépot.'
    )
    parser.add_argument('src_path', help='emplacement du dossier source')
    parser.add_argument('dest_path', help='emplacement du dossier destination')
    parser.add_argument('time_to_wait', help='temps d\attente en seconde entre chaque boucle', type=int)
    args = parser.parse_args()

    folder_path = args.src_path
    dest_path = args.dest_path

    logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(process)d) - %(levelname)s - %(message)s')

    elems_in_folder = {}

    while True:
        for elem in os.listdir(folder_path):
            elem = os.path.join(folder_path, elem)
            size = get_directory_size(elem)
            logging.debug(f'detect file {elem} of {size}b')
            if elem not in elems_in_folder: # si le fichier existe en FS mais pas en Set
                logging.debug(f'adding file {elem} to dict')
                elems_in_folder[elem] = size
            elif elems_in_folder[elem] != size: # si la taille du fichier a changer
                logging.debug(f'it was {elems_in_folder[elem]} and now {size}b')
                elems_in_folder[elem] = size
            elif size: # Si le fichier n'a pas change de taille mais que sa taille est superieur à 0
                logging.debug(f'Size stayed the same as before (now: {size}, before: {elems_in_folder[elem]}')
                move_to(elem, dest_path)
                del elems_in_folder[elem]

        elems_to_remove = []
        for path in elems_in_folder: # Retire les fichier qui sont dans le dict mais plus dans le FS
            if not os.path.exists(path):
                logging.debug(f'{path} was removed from outside')
                elems_to_remove.append(path)

        for path in elems_to_remove:
            del elems_in_folder[path]

        if not elems_in_folder: # s'il n'y a plus d'element dans dict
            break
        time.sleep(args.time_to_wait)

if __name__ == "__main__":
    main()
