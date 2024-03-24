import re
import sys
import shutil
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

images_files = list()
video_files = list()
documents_files = list()
audio_files = list()
archives_files = list()
folders = list()
other = list()
unknown = set()
extensions = set()

image_extensions = ['JPEG', 'PNG', 'JPG', 'SVG']
video_extensions = ['AVI', 'MP4', 'MOV', 'MKV']
audio_extensions = ['MP3', 'OGG', 'WAV', 'AMR']
documents_extensions = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
archives_extensions = ['ZIP', 'GZ', 'TAR']

list_of_all_extensions = (
    image_extensions + video_extensions +
    audio_extensions + documents_extensions +
    archives_extensions
)

registered_extensions = dict()
registered_extensions.update({i: 'images' for i in image_extensions})
registered_extensions.update({i: 'video' for i in video_extensions})
registered_extensions.update({i: 'audio' for i in audio_extensions})
registered_extensions.update({i: 'documents' for i in documents_extensions})
registered_extensions.update({i: 'archives' for i in archives_extensions})

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r",
               "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in list_of_all_extensions:
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            other.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                globals()[container + "_files"].append(new_name)
            except KeyError:
                unknown.add(extension)
                other.append(new_name)


def handle_file(path, root_folder, dist):
    print(f'Handle file {path} in th {threading.get_ident()}')
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name)
    new_path = target_folder / new_name

    print(f"Moving {path} to {new_path}")

    if path.exists():
        path.replace(new_path)
    else:
        print(f"Error: File {path} not found.")


def handle_archive(path, root_folder, dist):
    print(f'Handle archive {path} in th {threading.get_ident()}')
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    new_name = normalize(path.name.replace(".zip", '').replace('.tar', '').replace('.gz', ''))
    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        path.unlink()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        path.unlink()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)

    try:
        path.rmdir()
        print(f"Removed empty folder: {path}")
    except OSError as e:
        print(f"Error removing folder {path}: {e}")


def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)

    print(f'Start in {folder_path}')

    file_types = {
        'images': images_files,
        'documents': documents_files,
        'audio': audio_files,
        'video': video_files,
        'archives': archives_files,
        'other': other
    }

    # add threads
    with ThreadPoolExecutor() as executor:
        for file_type, files in file_types.items():
            for file in files:
                if file_type == 'archives':
                    executor.submit(handle_archive, file, folder_path, file_type)
                else:
                    executor.submit(handle_file, file, folder_path, file_type)

    remove_empty_folders(folder_path)

    # Rest of the code remains unchanged
    print("Contents of Organized Folders:")
    for item in folder_path.iterdir():
        if item.is_dir():
            print(f"Folder: {item}")
            for subitem in item.iterdir():
                print(f"  {subitem}")
        else:
            print(f"File: {item}")
    print(f'images: {[normalize(file.name) for file in images_files]}')
    print(f'video: {[normalize(file.name) for file in video_files]}')
    print(f'documents: {[normalize(file.name) for file in documents_files]}')
    print(f'audio: {[normalize(file.name) for file in audio_files]}')
    print(f'archives: {[normalize(file.name) for file in archives_files]}')
    print(f"other: {[normalize(file.name) for file in other]}")
    print(f"unknowns extensions: {[normalize(ext) for ext in unknown]}")
    print(f"unique extensions: {[normalize(ext) for ext in extensions]}")


if __name__ == '__main__':
   main()