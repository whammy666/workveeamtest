import os
import hashlib
import shutil
import time
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync.log"),
        logging.StreamHandler()
    ]
)


def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_hashes_of_files_in_folder(folder_path: str) -> dict[str, str]:
    files_hashes = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            files_hashes[relative_path] = get_file_hash(file_path)
    return files_hashes


def synchro_folders(source_folder_path: str, target_folder_path: str) -> None:
    global target_file_path
    source_file_hashes = get_hashes_of_files_in_folder(source_folder_path)
    target_file_hashes = get_hashes_of_files_in_folder(target_folder_path)

    for relative_path, source_hash in source_file_hashes.items():
        source_file_path = os.path.join(source_folder_path, relative_path)
        target_file_path = os.path.join(target_folder_path, relative_path)

        if relative_path not in target_folder_path:
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            shutil.copy2(source_file_path, target_file_path)
            logging.info(f"Copied: {source_file_path} to {target_file_path}")
        elif target_file_hashes[relative_path] != source_hash:
            shutil.copy2(source_file_path, target_file_path)
            logging.info(f"Updated: {target_file_path}")

    for relative_path in target_file_hashes.keys():
        if relative_path not in source_file_hashes:
            clone_file_path = os.path.join(target_folder_path, relative_path)
            os.remove(clone_file_path)
            logging.info(f"Deleted: {target_file_path}")


def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("target", help="Path to the target folder")
    parser.add_argument("-i", "--interval", type=int, default=900, help="Sync interval in seconds (default: 900)")

    args = parser.parse_args()

    source_folder_path = args.source
    target_folder_path = args.target
    sync_interval = args.interval

    while True:
        synchro_folders(source_folder_path, target_folder_path)
        time.sleep(sync_interval)


if __name__ == '__main__':
    main()