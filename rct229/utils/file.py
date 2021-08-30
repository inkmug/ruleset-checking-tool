import json
import os
from pathlib import Path


def deserialize_rmr_file(rmr_file):
    # with open(file_name) as f:
    if rmr_file:
        data = json.load(rmr_file)

        return data

    else:
        return None


def save_text_file(text_str, path, filename):
    out_name = os.path.join(path, filename)   

    # Create directory if it doesn't exist.
    Path(path).mkdir(parents=True, exist_ok=True)

    # Writing to text file 
    with open(out_name, "w") as outfile: 
        outfile.write(text_str)