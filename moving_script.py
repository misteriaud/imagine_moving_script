import os
import time
import shutil
import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

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
            shutil.move(self.path, new_path)
            logging.debug(f'move {self.path} to {new_path}')
        except shutil.Error as e:
            logging.error(f'error: couldn\'t move {self.path} to {new_path} ({e})')

def main():
    logging.info("start")
    folder_path = "src"
    dest_path = "dest"

    items = []
    for elem in os.listdir(folder_path):
        elem = os.path.join(folder_path, elem)
        items.append(Item(elem))

    while items:
        time.sleep(5)
        to_move = []
        for item in items:
            if (not item.has_changed()):
                to_move.append(item)
        for item in to_move:
            item.move_to(dest_path)
            items.remove(item)

    logging.info("end\n")

if __name__ == "__main__":
    main()

# to send email from synology nas: https://swisstechiethoughts.wordpress.com/2014/01/20/howto-send-mail-from-synology-nas-commandline-using-google-mail-relay/
