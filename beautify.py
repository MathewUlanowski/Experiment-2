import os
import json
import threading

def beautify_json_in_directory(folder_path: str, skip_beautify: bool = False) -> None:
    """
    Beautifies all JSON files in the specified directory unless skip_beautify is True.

    :param folder_path: Path to the directory containing JSON files.
    :param skip_beautify: If True, skips the beautification process.
    """
    if skip_beautify:
        print("Skipping JSON beautification as per the flag.")
        return

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping {file_path}: Unable to decode JSON.")
                    continue

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                    f.write('\n')

def beautify_json_async(folder_path: str) -> None:
    """
    Runs the beautify_json_in_directory function asynchronously on a separate thread.

    :param folder_path: Path to the directory containing JSON files.
    """
    thread = threading.Thread(target=beautify_json_in_directory, args=(folder_path,))
    thread.daemon = True  # Ensure the thread exits when the main program exits
    thread.start()
