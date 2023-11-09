import json

json_file_path = 'cookie.json'

def cookie_rewriter(new_cookie):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    if 'cookie_info' not in data or not data['cookie_info']:
        data['cookie_info'] = new_cookie

        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=2)

        return True
    else:
        return False

def cookie_validator():
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    if 'cookie_info' in data and data['cookie_info']:
        return data['cookie_info']
    else:
        return False
