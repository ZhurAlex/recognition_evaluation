import json

from picture_object import PictureObject


def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def prepare_json_data(json_data):
    meta = json_data[0]['objects']
    image_size = (json_data[0]["width"], json_data[0]["height"])
    geom = {o["nm"]: o for o in json_data[1]["objects"]}
    merged = [{"image_size": image_size, **m, **geom[m["nm"]]} for m in meta]

    return merged

def get_objects_from_json(json_folder, image_name):
    json_data = load_json(f'{json_folder}/{image_name}.json')
    masks_dir = f'{json_folder}/{image_name}.images/00001'
    prepared_data = prepare_json_data(json_data)
    objects = [PictureObject(obj, masks_dir) for obj in prepared_data]
    return objects
