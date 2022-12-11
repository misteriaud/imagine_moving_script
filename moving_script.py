import os
import time
import shutil

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
        print("init ", self.path, ": ", self.size)

    def has_changed(self):
        current_size = get_directory_size(self.path)
        if (self.size != current_size):
            self.size = current_size
            return True
        return False

    def move_to(self, new_path):
        try:
            shutil.move(self.path, new_path)
        except:
            print("error: couldn't move the file", self.path, "to", new_path)
        print("move", self.path, "to", new_path)

def main():
    folder_path = "."
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

if __name__ == "__main__":
    main()

# to send email from synology nas: https://swisstechiethoughts.wordpress.com/2014/01/20/howto-send-mail-from-synology-nas-commandline-using-google-mail-relay/
