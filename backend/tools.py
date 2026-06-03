import json


def json_to_dict(json_path: str) -> dict:
    result: dict = {}

    try:
        with open(json_path, encoding='utf-8') as json_file:
            result = json.load(json_file)
            json_file.close()

    except FileNotFoundError:
        pass

    return result


def dict_to_json(output_path: str, output_dict: dict) -> None:
    with open(output_path, "w", encoding='utf-8') as f:
        output: str = json.dumps(output_dict, indent=2, ensure_ascii=False)
        f.write(output)
        f.close()
