from typing import Any
from keybuilder import load_keys, get_spacing
from pprint import pp
from enum import Enum
from abc import ABC

object_dict = {}

def register(cls):
    object_dict[cls.__name__.lower()] = cls
    return cls

class BaseObject(ABC):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

@register
class AttackObject(BaseObject):
    def __init__(self, start_dict: dict):
        print("Making Attack Object")

@register
class DamageRollObject(BaseObject):
    def __init__(self, start_string: str):
        print("Making Damage Roll Object")

@register
class ArmyKillsObject(BaseObject):
    def __init__(self, start_dict: dict):
        print("Making Army Kills")

def object_creator(typ: str, *args)->BaseObject:
    if typ not in object_dict:
        raise KeyError
    return object_dict[typ](args)

def sub_basis(basis: dict, keys: list)->tuple[bool, dict]:
    curr = basis
    for key in keys:
        if key in curr:
            curr = curr[key]
        else:
            return (False, "")
    return (True, curr) #Maybe?


def build_tree(file:str="samplefile.txt")->dict:
    basis = load_keys()
    tree = {}
    with open(file, 'r') as fin:
        spacing = [0]   #Track Spacing
        result = {} # Essentially Place each Character into this
        to_build = []   #Stores the info of building the tree - Will create Dictionaries
        previous_key = []
        tracker = []
        number = 0
        for line in fin:
            number += 1
            if line.isspace():
                continue
            data = line.strip().split(':')
            for i in range(len(data)):
                data[i] = data[i].strip()
            
            if get_spacing(line) > spacing[-1]:
                if len(to_build) > 0:
                    tracker.append(previous_key[-1])
                to_build.append({'KEY':previous_key[-1]})
                spacing.append(get_spacing(line))
                
            elif len(previous_key) != 0:
                previous_key.pop()       

            while get_spacing(line) < spacing[-1]:
                if len(spacing) > 2: 
                    #Handle if it should be an object or not here
                    _, sub_tree = sub_basis(basis, tracker)
                    key_value = to_build[-1]['KEY']
                    if 'TYPE' in sub_tree:
                        if sub_tree['TYPE'] == 'Object':
                            try:
                                to_build[-2][previous_key[-1]] = object_creator(previous_key[-1].lower()+'object', to_build[-1])
                            except Exception as e:
                                print(f"Invalid type! {previous_key[-1]} must be Class Definition - Not found, got {to_build} ending on line {number}. Skipping...") 

                        else:
                            to_build[-2][key_value] = to_build[-1]
                            to_build[-2][key_value].pop('KEY', None)  
                    tracker.pop()       
                else:
                    result[previous_key[-1]] = to_build[-1]
                    result[previous_key[-1]].pop('KEY', None)    #Make it so that it isn't redundant
                    tracker = []    #Empty out Tracker
                to_build.pop()
                spacing.pop()
                previous_key.pop()   
            
            previous_key.append(data[0])    
            if data[1] == '':
                #May need to test if there is just a space
                continue
            tracker.append(data[0])
            valid, sub_tree = sub_basis(basis, tracker)
            tracker.pop()
            if not valid:
                print(f"{data} NOT VALID IN {tracker}")
                previous_key.pop()
                continue

            #Type Check/Handle the different types appropriately
            if 'TYPE' in sub_tree:
                if sub_tree['TYPE'] == 'Int':
                    try:
                        to_build[-1][data[0]] = int(data[1])
                    except:
                        print(f"Invalid type! {data[0]} must be Int type, got {data[1]} instead on line {number}. Skipping...")
                elif sub_tree['TYPE'] == 'String':
                    try:
                        to_build[-1][data[0]] = data[1]
                    except:
                        print(f"Invalid type! {data[0]} must be String type, got {data[1]} instead on line {number}. Skipping...") 
                elif sub_tree['TYPE'] == 'Object':
                    try:
                        to_build[-1][data[0]] = object_creator(data[0].lower()+'object', data[1:])
                    except:
                        print(f"Invalid type! {data[0]} must be Class Definition - Not found, got {data} on line {number}. Skipping...") 
       
                elif issubclass(sub_tree['TYPE'], Enum):
                    temp = False
                    for j in sub_tree['TYPE']:
                        if data[1].upper() ==  j.name.upper():
                            #print(f"Made a {j} enum!")
                            to_build[-1][data[0]] = j  
                            temp = True
                    if not temp:
                        print(f"Invalid ENUM value! Should be {sub_tree['TYPE']}, Found {data} on line {number}")
                 #Handle the last instance
        previous_key.pop()
        while len(previous_key) != 0:
            if len(previous_key) > 1:
                _, sub_tree = sub_basis(basis, tracker)
                key_value = to_build[-1]['KEY']
                if 'TYPE' in sub_tree:
                    if sub_tree['TYPE'] == 'Object':
                        to_build[-2][key_value] = object_creator(key_value.lower()+'object', to_build[-1])
                        # Handle the popping and all other stuff in object 
                    else:
                        to_build[-2][key_value] = to_build[-1]
                        to_build[-2][key_value].pop('KEY', None)     
            else:
                result[previous_key[-1]] = to_build[-1]
                result[previous_key[-1]].pop('KEY', None)    #Make it so that it isn't redundant
            to_build.pop()
            previous_key.pop()
        return result
                

def main():
    pp(build_tree())

if __name__ == "__main__":
    main()
