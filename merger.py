import json
import os



subdirectory = "results"
filename = "result"
extension = ".json"

data = []

for i in range(1121):
    path = os.path.join(subdirectory, f'{filename}{i}{extension}')
    with open(path, 'r', encoding='utf-8') as file:
        print(f'Opening file {i}')
        file_json = json.load(file)
        data += file_json['data']

path = os.path.join(subdirectory,'result.json')
json_format = {'data': data}
with open(path, 'w', encoding='utf-8') as file:
    json.dump(json_format, file, ensure_ascii=False, indent=4)
