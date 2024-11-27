from keybuilder import load_keys, get_spacing
from enum import Enum
from fileloader import build_tree, BaseObject

def save_dict(dictionary: dict, file:str = 'demo.txt'):
    key_basis = load_keys()
    with open('demo.txt', 'w') as fout:
        spacing = [4]
        for key in dictionary:
            print(f"{key}:", file=fout)
            for sub_key in dictionary[key]:
                print(dictionary[key][sub_key])
                if sub_key in key_basis:
                    if isinstance(dictionary[key][sub_key], str) or isinstance(dictionary[key][sub_key], int):
                        spaces = " " * spacing[-1]
                        print(f"{spaces}{sub_key}:{dictionary[key][sub_key]}", file=fout)
                    elif isinstance(dictionary[key][sub_key], dict):
                        pass
                    elif isinstance(dictionary[key][sub_key], BaseObject):
                        print(dictionary[key][sub_key].to_file(spacing[-1]), file=fout)
                    elif issubclass(key_basis[sub_key]['TYPE'], Enum):
                        spaces = " " * spacing[-1]
                        print(f"{spaces}{sub_key}:{dictionary[key][sub_key].name}", file=fout)
                else:
                    print(f"INVALID KEY TRYING TO BE SAVED {sub_key} in {key}")

def main():
    tree = build_tree()
    save_dict(tree)

if __name__ == '__main__':
    main()