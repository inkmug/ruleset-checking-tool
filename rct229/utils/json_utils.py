import json
import os
from pathlib import Path


def save_json(obj, path, filename):
    out_name = os.path.join(path, filename)
    myjson = json.dumps(obj, indent=4)

    # Create directory if it doesn't exist.
    Path(path).mkdir(parents=True, exist_ok=True)

    # Writing to .json
    with open(out_name, "w") as outfile:
        outfile.write(myjson)


def load_json(json_file_path):
    with open(json_file_path) as f:
        return json.load(f)


def slash_prefix_guarantee(str):
    """Guarantees that a string starts with a slash by prepending one if
    not already present

    Parameters
    ----------
    str : string

    Returns
    -------
    string
        The original string possibly prepended with a slash if it did not
        already start with one
    """
    return str if len(str) is 0 or str[0] is "/" else "/" + str
