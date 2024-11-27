from typing import Any
from keybuilder import load_keys, get_spacing
from pprint import pp
from enum import Enum
from abc import ABC
from random import randint
from typing import Self
#Globals for various purposes
object_dict = {}
basis = {}

class DamageType:
    def __init__(self, default:Enum, amount: str, d_type=None) -> None:
        self.amount = amount
        if d_type is not None:
            temp = False
            for j in basis['DamageRoll']['DamageType']['TYPE']:
                if d_type.upper() == j.name.upper():
                    self.d_type = j  
                    temp = True
                    return
            if not temp:
                print(f"Invalid ENUM value! Should be {basis['DamageRoll']['DamageType']['TYPE']}, Found {d_type}")
                raise KeyError
        else:
            self.d_type = default
    def to_file(self)->str:
        temp = ""
        if self.d_type is not None:
            temp = '#' + self.d_type.value
        return str(self.amount) + temp
    def __str__(self) -> str:
        return f"{self.amount} : {self.d_type}"

    def __call__(self, *args: Any, **kwds: Any) -> tuple[list[int], Enum]:
        if 'd' in self.amount:
            rolls = []
            nDice, nDieRoll = self.amount.split('d')
            for _ in range(int(nDice)):
                rolls.append(randint(1, int(nDieRoll)))
            return rolls, self.d_type 
            #Roll then give result
        elif self.amount[0] == '.':
            return [self.amount[1:]], self.d_type
        else:
            return [int(self.amount)], self.d_type


def register(cls):
    object_dict[cls.__name__.lower()] = cls
    return cls

class BaseObject(ABC):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
    def to_file(space_start: int)->str:
        pass
class DictObject(BaseObject):
    def __init__(self, start_dict: dict) -> None:
        self.dict_object = start_dict[0]

@register
class AttackObject(DictObject):
    def __init__(self, start_dict: dict):
        super().__init__(start_dict)
        if 'Bonus' not in self.dict_object:
            self.dict_object['Bonus'] = 0
        if 'BaseType' not in self.dict_object:
            self.dict_object['BaseType'] = basis['Attack']['BaseType']['TYPE'].Bludgeoning
            #Default BaseType
        if 'DamageRoll' not in self.dict_object:
            self.dict_object['DamageRoll'] = DamageRollObject("1d4")

    def to_file(space_start: int)->str:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> tuple[int, list[DamageType]]:
        #Returns the roll, and the damage if hit - the breakdown
        if 'DamageRoll' in self.dict_object and 'BaseType' in self.dict_object:
            result = self.dict_object['DamageRoll'](self.dict_object['BaseType'])
            filled = []
            for i in range(len(result)): 
                if result[i][1] is None:
                    filled.append((result[i][0], self.dict_object['BaseType']))
                else:
                    filled.append(result[i])
        return randint(1, 20) + self.dict_object['Bonus'], filled
    
    def __str__(self) -> str:
        return str(self.dict_object)
    
    def __repr__(self) -> str:
        return repr(self.dict_object)

@register
class DamageRollObject(BaseObject):
    def __init__(self, start_string: str):
        #Need to make Roll
        self._damage_rolls = []
        adds_string = start_string[0]['Value'].split('+')
        for sub in adds_string:
            temp = sub.split('#')#Use the # to identify the different types I think?
            if len(temp) > 1:
                self._damage_rolls.append(DamageType(None, temp[0], temp[1]))
            else:
                self._damage_rolls.append(DamageType(None, temp[0]))#Change None to the default somehow
        #print("Making Damage Roll Object")
    
    def __str__(self) -> str:
        string = f"<Damage Roll Object: Rolls: "
        for rolls in range(len(self._damage_rolls)):
            string += str(self._damage_rolls[rolls]) + ', '
        string = string[:-2]
        string += '>'
        return string

    def __repr__(self) -> str:
        return str(self)        

    def __call__(self, *args: Any, **kwds: Any) -> list[tuple[int, Enum]]:
        roll = []
        for rolls in self._damage_rolls:
            roll.append(rolls())
        return roll

@register
class ArmyKillsObject(DictObject):
    def __init__(self, start_dict: dict):
        super().__init__(start_dict)
        #print("Making Army Kills")
    
    def __call__(self, other:Self)->int:
        roll = max(0, randint(1, 20) + self.dict_object['Bonus'] - other.dict_object['Bonus'])
        mult = max(1, self.dict_object['BaseDamageMultiplier'] - other.dict_object['BaseDamageMultiplier'])
        return roll * mult

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
    global basis
    basis = load_keys()
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
                elif sub_tree['TYPE'] == 'List':
                    to_build[-1][data[0]] = data[1].split('-')
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

class UnitTracker:
    def __init__(self, start_dict: dict) -> None:
        self.units = {}
        self.army_units = {}
        self.last_unit_dmg = []
        self.last_army_dmg = []
        self.unit_breakdown = []
        self.army_breakdown = []
        pass         

    def roll_attack(self, target: str)->tuple[int, list[DamageType], int]:
        #Returns the attack roll, the attack breakdown and the total damage
        attack, damage = self.units[target]['Attack']()
        #Check for Stats
        total_damage = 0
        for rolls in range(len(damage)):
            for each_roll in range(len(damage[rolls][0])):
                if isinstance(damage[rolls][0][each_roll], str):
                    #Parse Variable
                    temp = list(damage[rolls])
                    info = temp[0][each_roll].split('.')
                    if info[0] == 'Stats':
                        temp[0][each_roll] = (self.units[target]['Stats'][info[1]] - 10) // 2 
                        total_damage += temp[0][each_roll]
                    else:
                        print("Not yet implemented for using something else")
                        break
                    damage[rolls] = tuple(temp)
                else:
                    total_damage += damage[rolls][0][each_roll]
        return (attack, damage, max(0, total_damage))

    def roll_army_attack(self, source: str, target:str)->int:
        dmg = self.army_units[source]['ArmyKills'](self.army_units[target]['ArmyKills']) 
        return dmg

    def attack(self, source: str, target:str)->dict:
        global last_dmg, breakdown
        if 'ArmyKills' in source and 'ArmyKills' in target:
            dmg, target = self.roll_army_attack(source, target)
        elif 'Attack' in source and 'Attack' in target:
            tohit, _breakdown, dmg = self.roll_attack(source)
            self.unit_breakdown.append(_breakdown)
            self.last_unit_dmg.append(dmg)
            #Calculate damage to target then return target
        return target

def main():
    sampletree = build_tree() 
    pp(sampletree)
    print(sampletree['drow1']['Attack']())
    print(sampletree['drow2']['Attack']())
    #print(roll_attack(sampletree['drow2']))
    print(sampletree['drowarmy1']['ArmyKills'](sampletree['drowarmy1']['ArmyKills']))
    #print(roll_army_attack(sampletree['drowarmy1'], sampletree['drowarmy1']))
    

if __name__ == "__main__":
    main()
