import os
import time
import shutil
import logging
import argparse


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

class Item:

    def __init__(self, path):
        self.path = path
        self.size = get_directory_size(path)
        logging.debug(f'detect {self.path} ({self.size}B)')

    def has_changed(self):
        current_size = get_directory_size(self.path)
        if (self.size != current_size):
            self.size = current_size
            return True
        return False

    def move_to(self, new_path):
        try:
            new_path = shutil.move(self.path, new_path)
            shutil.chown(new_path, "l.torti", group="GRP_NAS_Tampon")
            logging.debug(f'move {self.path} to {new_path}')
        except shutil.Error as e:
            logging.error(f'error: couldn\'t move {self.path} to {new_path} ({e})')

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

    items = []
    for elem in os.listdir(folder_path):
        elem = os.path.join(folder_path, elem)
        items.append(Item(elem))

    while items:
        time.sleep(args.time_to_wait)
        moved_items = []
        for item in items:
            try:
                if (not item.has_changed()):
                    item.move_to(dest_path)
                    moved_items.append(item)
            except:
                moved_items.append(item)
        for moved_item in moved_items:
            items.remove(moved_item)

if __name__ == "__main__":
    main()

# to send email from synology nas: https://swisstechiethoughts.wordpress.com/2014/01/20/howto-send-mail-from-synology-nas-commandline-using-google-mail-relay/
