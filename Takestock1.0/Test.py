from flask import Flask, url_for

app = Flask(__name__)

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

nested_dict = {
    'a': 1,
    'b': {
        'c': 2,
        'd': {
            'e': 3
        }
    }
}
def unflatten_dict(d, sep='_'):
    result_dict = {}
    for key, value in d.items():
        parts = key.split(sep)
        d = result_dict
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return result_dict
"""
flattened_dict = {
    'a': 1,
    'b_c': 2,
    'b_d_e': 3
}
"""
print(nested_dict)
flattened_dict = flatten_dict(nested_dict)
print(flattened_dict)
original_dict = unflatten_dict(flattened_dict)
print(original_dict)
