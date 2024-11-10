import json

def load_data(file_path):
    """
    Load data from a JSON file.

    Parameters
    ----------
    file_path : str
        The path to the JSON file to be loaded.

    Returns
    -------
    dict
        The data loaded from the JSON file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    json.JSONDecodeError
        If the file is not a valid JSON.
    """
    with open(file_path, "r") as f:
        return json.load(f)