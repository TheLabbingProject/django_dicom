import json
import numpy as np


def snake_case_to_camel_case(string: str) -> str:
    return "".join([part.title() for part in string.split("_")])


class NumpyEncoder(json.JSONEncoder):
    """
    Converts NumPy array to a JSON serializable nested list.
    Based on this_ SO answer.

    .. _this: https://stackoverflow.com/a/47626762
    
    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
