from typing import Any
from keybuilder import load_keys, get_spacing
from pprint import pp
from enum import Enum
from abc import ABC
from random import randint
from typing import Self
from copy import deepcopy
#Globals for various purposes
object_dict = {}
basis = {}

class DamageType:
    def __init__(self, default:Enum, amount: str, d_type=None) -> None:
        self.amount = amount
        if d_type is not None:
            temp = False
            for j in basis['Attack']['DamageRoll']['DamageType']['TYPE']:
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
            temp = '#' + self.d_type.name
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
        self.dict_object.pop('KEY', None)
    def __str__(self) -> str:
        return str(self.dict_object)
    def __repr__(self) -> str:
        return repr(self.dict_object)
    def to_file(self, start_space:int)->str:
        space = " " * start_space
        string = ""
        for key in self.dict_object:
            if key == key.upper():
                continue
            if isinstance(self.dict_object[key], BaseObject):
                string += self.dict_object[key].to_file(start_space)
            elif isinstance(self.dict_object[key], Enum):
                string += space + f"{key}: {self.dict_object[key].name}\n"
            elif isinstance(self.dict_object[key], list):
                string += ' ' * 4 + f"{key}: " + '-'.join(self.dict_object[key])+"\n"
            else:
                string += space + f"{key}: {self.dict_object[key]}\n"
        return string

@register
class AttackObject(DictObject):
    def __init__(self, start_dict: dict):
        super().__init__(start_dict)
            #Default BaseType

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
        return randint(1, 20) + self.dict_object['AttackBonus'], filled

@register
class DamageRollObject(BaseObject):
    def __init__(self, start_string: str):
        #Need to make Roll
        self._damage_rolls = []
        adds_string = start_string[0]['Value'].split('+')
        for sub in adds_string:
            temp = sub.split('#')                                       #Use the # to identify the different types I think?
            if len(temp) > 1:
                self._damage_rolls.append(DamageType(None, temp[0], temp[1]))
            else:
                self._damage_rolls.append(DamageType(None, temp[0]))    #None gets changed when attacking
    
    def __str__(self) -> str:
        string = f"<Damage Roll Object: Rolls: "
        for rolls in range(len(self._damage_rolls)):
            string += str(self._damage_rolls[rolls]) + ', '
        string = string[:-2]
        string += '>'
        return string

    def to_file(self, space_start: int)->str:
        space = ' ' * space_start
        indent = ' ' * (space_start + 4)
        string = space + 'DamageRoll:\n'
        sub = '+'.join(list(map(lambda x: x.to_file(), self._damage_rolls)))
        string += indent + 'Value:' + sub + '\n'
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
    
    def __call__(self, other:Self)->int:
        roll = max(0, randint(1, 20) + self.dict_object['Bonus'] - other.dict_object['Bonus'])
        mult = max(1, self.dict_object['BaseDamageMultiplier'] - other.dict_object['BaseDamageMultiplier'])
        return roll, mult, roll * mult

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

def add_int(base_dict:dict, key:str, intstring: str, number: int = 0)->dict:
    if key in base_dict:
        print(f'{key} ALREADY DEFINED: SKIPPING')
        return base_dict
    try:
        base_dict[key] = int(intstring)
    except:
        print(f"Invalid type! {key} must be Int type, got {intstring} instead on line {number}. Skipping...")
    return base_dict

def add_str(base_dict: dict, key: str, string: str, number: int = 0)->dict:
    if key in base_dict:
        print(f'{key} ALREADY DEFINED: SKIPPING')
        return base_dict
    try:
        base_dict[key] = string
    except:
        print(f"Invalid type! {key} must be String type, got {string} instead on line {number}. Skipping...") 
    return base_dict

def add_enum(base_dict:dict, key:str, enum_val: str, enum_decl: Enum, number: int = 0)->dict:
    for j in enum_decl:
        if enum_val.upper() ==  j.name.upper():
            base_dict[key] = j  
            return base_dict
    print(f"Invalid ENUM value! Should be {enum_decl}, Found {key} : {enum_val} on line {number}")
    return base_dict

def add_dict(base_dict: dict, key: str, value: dict, number: int=0)->dict:
    for sub_key in basis[key]:
        if sub_key not in value and isinstance(basis[key][sub_key], dict) and 'GENERATE' in basis[key][sub_key]:
            generator = basis[key][sub_key]
            is_dict = 'TYPE' in basis[key][sub_key] and basis[key][sub_key]['TYPE'] == 'Dictionary'
            if generator == True:
                # It's an object so make it based off of the Default values
                generator = add_object({}, sub_key, {}, [sub_key], number)
                value[sub_key] = generator[sub_key]        
                continue
            elif '.' in generator:
                if generator[1:] not in value:
                    print(f'CAN NOT FIND VARIABLE TO USE AS GENERATOR {generator} in {value}')
                    raise KeyError(f'CAN NOT FIND VARIABLE TO USE AS GENERATOR {generator} in {value}')
                generator = value[generator[1:]]
            elif is_dict:
                generator = add_dict({}, sub_key, {}, number)
                value[sub_key] = generator[sub_key]
                continue
            else:
                value = add_base_on_type(value, generator, sub_key, generator['GENERATE'], number)


    base_dict[key] = value
    base_dict[key].pop('KEY', None) 
    return base_dict 

def add_base_on_type(base_dict:dict, sub_tree: dict, key: str, value: str|dict, number: int = 0, path:list=None)->dict:
    if 'TYPE' in sub_tree:
        if sub_tree['TYPE'] == 'Int':
            base_dict = add_int(base_dict, key, value, number)
        elif sub_tree['TYPE'] == 'String':
            base_dict = add_str(base_dict, key, value, number)
        elif sub_tree['TYPE'] == 'List':
            base_dict[key] = value.split('-')
        elif sub_tree['TYPE'] == 'Object':
            base_dict = add_object(base_dict, key, value, path, number)
        elif sub_tree['TYPE'] == 'Dictionary':
            base_dict = add_dict(base_dict, key, value, number)
        elif issubclass(sub_tree['TYPE'], Enum):
            base_dict = add_enum(base_dict, key, value, sub_tree['TYPE'], number)
            #Handle the last instance
    return base_dict

def add_object(base_dict: dict, key:str, info:dict, path: list,number: int =0)->dict:
    try:
        _, sub = sub_basis(basis, path)
        eithers = False
        for sub_key in sub:
            if sub_key not in info and isinstance(sub[sub_key], dict) and 'REQUIRED' in sub[sub_key]:
                print(f'MISSING REQUIRED KEY: {key} in {sub_key} finished on line {number}')
                all_reqs = False
                raise KeyError(f'MISSING REQUIRED KEY: {key} in {sub_key} finished on line {number}')
            elif sub_key in info and isinstance(sub[sub_key], dict) and 'EITHER' in sub[sub_key]:
                if eithers:
                    print(f'CAN NOT HAVE MULTIPLE EITHER VALUES {sub_key} in {key} finished on line {number}')
                    raise KeyError(f'CAN NOT HAVE MULTIPLE EITHER VALUES {sub_key} in {key} finished on line {number}')
                else:
                    eithers = True
        for sub_key in sub:
            if sub_key not in info and isinstance(sub[sub_key], dict) and 'GENERATE' in sub[sub_key]:
                if sub[sub_key]['GENERATE'] == True:
                    info = add_base_on_type(info, sub[sub_key], sub_key, {}, number, path+[sub_key])
                else:
                    info = add_base_on_type(info, sub[sub_key], sub_key, sub[sub_key]['GENERATE'], number, path+[sub_key])

        base_dict[key] = object_creator(key.lower()+'object', info)
    except Exception as e:
        print(f"Invalid type! {key} must be Class Definition - Not found, got {info} on line {number}. Skipping...") 
    return base_dict            

def complete_unit(base_dict: dict, add_key: str, to_add: dict, number:int = 0):
    all_reqs = True 
    eithers = False
    for key in basis:
        if 'REQUIRED' in basis[key]:
            if key not in to_add:
                print(f'MISSING REQUIRED KEY: {key} in {add_key} finished on line {number}')
                all_reqs = False
                raise KeyError(f'MISSING REQUIRED KEY: {key} in {add_key} finished on line {number}')
        elif 'EITHER' in basis[key]:
            if key in to_add and eithers:
                print(f'CAN NOT HAVE MULTIPLE EITHER VALUES {key} in {add_key} finished on line {number}')
                raise KeyError(f'CAN NOT HAVE MULTIPLE EITHER VALUES {key} in {add_key} finished on line {number}')
            elif key in to_add:
                eithers = True
    for sub_key in basis:
        if sub_key not in to_add and isinstance(basis[sub_key], dict) and 'GENERATE' in basis[sub_key]:
            generator = basis[sub_key]
            is_dict = 'TYPE' in basis[sub_key] and basis[sub_key]['TYPE'] == 'Dictionary'
            sub_tree_var = basis[sub_key]['TYPE']
            if generator == True:
                # It's an object so make it based off of the Default values
                generator = add_object({}, sub_key, {}, [sub_key], number)
                to_add[sub_key] = generator[sub_key]        
                continue
            elif isinstance(generator['GENERATE'], str) and '.' in generator['GENERATE']:
                #Make it so that it can "Search" More for Variables
                if generator['GENERATE'][1:] not in to_add:
                    print(f'CAN NOT FIND VARIABLE TO USE AS GENERATOR {generator} in {to_add}')
                    raise KeyError(f'CAN NOT FIND VARIABLE TO USE AS GENERATOR {generator} in {to_add}')
                generator = to_add[generator['GENERATE'][1:]]
                sub_tree_var = {'TYPE':sub_tree_var}
            elif is_dict:
                sub_tree_var = basis[sub_key]
                generator = add_dict({}, sub_key, {}, number)
                to_add[sub_key] = generator[sub_key]
                continue
            else:
                if sub_tree_var == 'Int':
                    generator = basis[sub_key]['GENERATE']
                    sub_tree_var = {'TYPE': 'Int'}
                elif sub_tree_var == 'String':
                    generator = basis[sub_key]['GENERATE']
                    sub_tree_var = {'TYPE': 'String'}
                elif issubclass(sub_tree_var, Enum):
                    generator = basis[sub_key]['GENERATE']
                    sub_tree_var = {'TYPE':sub_tree_var}

            to_add = add_base_on_type(to_add, sub_tree_var, sub_key, generator, number)
    if not all_reqs:
        pass
    base_dict[add_key] = to_add
    base_dict[add_key].pop('KEY', None)
    return base_dict 

def build_tree(file:str="samplefile.sfs")->dict:
    global basis
    basis = load_keys()
    with open(file, 'r') as fin:
        spacing = [0]       # Track Spacing
        result = {}         # Essentially Place each Character into this
        to_build = []       # Stores the info of building the tree - Will create Dictionaries
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
                    to_build[-2] = add_base_on_type(to_build[-2], sub_tree, key_value, to_build[-1], number, tracker)
                    tracker.pop()       
                else:
                    #Go through and check any required ones, and either ones
                    result = complete_unit(result, previous_key[-1], to_build[-1], number)
                    tracker = []                                    # Empty out Tracker
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
            to_build[-1] = add_base_on_type(to_build[-1], sub_tree, data[0], data[1], number) 
            #Handle the last instance
        previous_key.pop()
        while len(previous_key) != 0:
            if len(previous_key) > 1:
                _, sub_tree = sub_basis(basis, tracker)
                key_value = to_build[-1]['KEY']
                to_build[-2] = add_base_on_type(to_build[-2], sub_tree, key_value, to_build[-1], number, tracker)
            else:
                result = complete_unit(result, previous_key[-1], to_build[-1], number)
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
        for unit in start_dict:
            if 'Attack' in start_dict[unit]:
                self.units[unit] = start_dict[unit]
            elif 'ArmyKills' in start_dict[unit]:
                self.army_units[unit] = start_dict[unit]
            else:
                print(f"INVALID UNIT! {start_dict[unit]}")
                raise KeyError(f"{start_dict[unit]['Name']} IS not valid - missing Attack/ArmyKills Tag")
        self.basis = basis

    def __str__(self) -> str:
        to_make = "Units:\n"
        for i in self.units:
            to_make += str(self.units[i]) + '\n'
        to_make += 'Army Units:\n'
        for i in self.army_units:
            to_make += str(self.army_units[i]) + '\n'
        to_make += 'Unit Damage Breakdown:\n'
        for i in self.last_unit_dmg:
            to_make += i + '\n'
        to_make += 'Army Unit Damage Breakdown:\n'
        for i in self.last_army_dmg:
            to_make += i 
        to_make += 'Unit Breakdown\n'
        for i in self.unit_breakdown:
            to_make += i + '\n'
        to_make += 'Army Unit Breakdown\n'
        for i in self.army_breakdown:
            to_make += i + '\n'
        return to_make
    
    def dict_key_valid(tester, typ)->bool:
        if typ.lower() == type(tester).__name__.lower():
            return True
        return False
    
    def enum_key_valid(enums, typ)->bool:
        for e in typ:
            if enums.lower() == e.name.lower():
                return True
        return False
    
    def display(self, unit:dict, key: str)->str:
        #return key
        print('NEW DISPLAY')
        print(str(unit[key]).replace('{', '').replace('}', '').replace('\n', ' ').replace("'", "").replace('"', ''))
        return str(unit[key]).replace('{', '').replace('}', '').replace('\n', ' ').replace("'", "").replace('"', '')
    
    def dict_to_file(unit_dict: dict, basis: dict)->str:
        string = ""
        for i in unit_dict:
            string += f"{i}:\n"
            for subkey in unit_dict[i]:
                key_exists, key_basis = sub_basis(basis, [subkey])
                if not key_exists:
                    print(f"SAVING KEY NOT FOUND! {subkey} in {i}")
                    continue

                if isinstance(unit_dict[i][subkey], BaseObject):
                    if not UnitTracker.dict_key_valid(unit_dict[i][subkey], object_dict[subkey.lower()+'object'].__name__):
                        print(f"INVALID SAVING TYPE: {subkey} in {i} should be type {key_basis['TYPE']}")
                        continue
                    string += ' ' * 4 + f"{subkey}:\n"
                    string += unit_dict[i][subkey].to_file(8)
                elif isinstance(unit_dict[i][subkey], Enum):
                    if not UnitTracker.enum_key_valid(unit_dict[i][subkey].name, key_basis['TYPE']): 
                        print(f"SAVING INVALID TYPE: {subkey} in {i}")
                        continue
                    string += ' ' * 4 + f"{subkey}: {unit_dict[i][subkey].name}\n"
                elif isinstance(unit_dict[i][subkey], dict):
                    string += ' ' * 4 + f"{subkey}:\n"
                    for tertiary_key in unit_dict[i][subkey]:
                        exists, basis_sub = sub_basis(basis, [subkey, tertiary_key])
                        if not exists:
                            print(f"SAVING Key not Found! {tertiary_key} in {subkey} in {i}")
                            continue
                        if not UnitTracker.dict_key_valid(unit_dict[i][subkey][tertiary_key], basis_sub['TYPE']): 
                            print(f"SAVING INVALID TYPE: {tertiary_key} in {subkey} in {i}")
                            continue
                        string += ' ' * 8 + f"{tertiary_key}: {unit_dict[i][subkey][tertiary_key]}\n"
                elif isinstance(unit_dict[i][subkey], list):
                    if not UnitTracker.dict_key_valid(unit_dict[i][subkey], key_basis['TYPE']):
                        print(f"INVALID SAVING TYPE: {subkey} in {i} should be type {key_basis['TYPE']}")
                    string += ' ' * 4 + f"{subkey}: " + '-'.join(unit_dict[i][subkey])+"\n"
                else:
                    if key_basis['TYPE'] == 'String':   #Little janky
                        key_basis['TYPE'] = 'str'
                    if not UnitTracker.dict_key_valid(unit_dict[i][subkey], key_basis['TYPE']): 
                        print(f"SAVING INVALID TYPE: {tertiary_key} in {subkey} in {i}")
                        continue
                    string += ' ' * 4 + f"{subkey}: {unit_dict[i][subkey]}\n"
        return string

    def to_file(self, basis: dict)->str:
        string = ""
        string += UnitTracker.dict_to_file(self.units, basis)
        string += UnitTracker.dict_to_file(self.army_units, basis)
        return string
    
    def save(self, basis: dict, file:str="demo.sfs")->None:
        with open(file, 'w') as fout:
            print(self.to_file(basis), file=fout)
        file = file[:-3] + 'info'   #Save the other infor as a .info
        with open('INFODUMP'+file, 'a') as fout:
            print(f"Army Breakdown: {'\n'.join(self.army_breakdown)}", file=fout)
            print(f"Army Damage: {'\n'.join(self.last_army_dmg)}", file=fout)
            print(f"Unit Breakdown: {'\n'.join(self.unit_breakdown)}", file=fout)
            print(f"Unit Damage: {'\n'.join(self.last_unit_dmg)}", file=fout)
    
    def roll_attack(self, target: dict)->tuple[int, list[DamageType], int]:
        #Returns the attack roll, the attack breakdown and the total damage
        attack, damage = target['Attack']()
        #Check for Stats
        total_damage = 0
        for rolls in range(len(damage)):
            for each_roll in range(len(damage[rolls][0])):
                if isinstance(damage[rolls][0][each_roll], str):
                    #Parse Variable
                    temp = list(damage[rolls])
                    info = temp[0][each_roll].split('.')
                    if info[0] == 'Stats':
                        temp[0][each_roll] = (target['Stats'][info[1]] - 10) // 2 
                        total_damage += temp[0][each_roll]
                    else:
                        print("Not yet implemented for using something else")
                        break
                    damage[rolls] = tuple(temp)
                else:
                    total_damage += damage[rolls][0][each_roll]
        return (attack, damage, max(0, total_damage))

    def roll_army_attack(self, source: dict, target:dict)->dict:
        roll, mult, total = source['ArmyKills'](target['ArmyKills']) 
        target['CurrentHp'] -= total
        self.army_breakdown.append(f"Army {source['Name']} attacks {target['Name']}: Deals {roll} * {mult} ({total}): Remaining HP: {target['CurrentHp']}")
        self.last_army_dmg.append(f"Total Damage: {total} Breakdown: {roll} * {mult}")
        return target

    def attack_targets(self, source:dict, target:dict)->dict:
        if 'ArmyKills' in source and 'ArmyKills' in target:
            self.target = self.roll_army_attack(source, target)
        elif 'Attack' in source and 'Attack' in target:
            tohit, _breakdown, dmg = self.roll_attack(source)
            if tohit >= target['AC'] and tohit != 1:    #Miss on 1's
                target = self.deal_unit_damage(target, _breakdown, dmg, source['Name'])
            else:
                self.unit_breakdown.append(f"ATTACK MISSED: {tohit} vs {target['AC']} - {source['Name']} vs {source['Name']}")
            #Calculate damage to target then return target
        return target

    def attack(self, source: str, target:str)->dict:
        if source in self.units and target in self.units:
            self.units[target] = self.attack_targets(self.units[source], self.units[target])
        elif source in self.army_units and target in self.army_units:
            self.army_units[target] = self.attack_targets(self.army_units[source], self.army_units[target])

    def get_damage_type(self, base: str)->Enum:
        print(base)
        for i in self.basis['Attack']['DamageRoll']['DamageType']['TYPE']:
            if i.name.upper() == base.upper():
                return i 
        return self.basis['Attack']['DamageRoll']['DamageType']['TYPE']['Bludgeoning']

    def deal_unit_damage(self, target: dict, breakdown: list[tuple[list[int], Enum]], dmg:int, source: str)->None:
        temp_resist = deepcopy(target['Resistances'])
        details = f"{source} Deals damage to {target['Name']}: Received "
        if sum(temp_resist.values()) > 0 or dmg < 0:
            for roll in breakdown:
                total = sum(roll[0])
                string = f"{'+'.join(map(str, roll[0]))} {roll[1].name} ({total})"
                if temp_resist[roll[1].name] > 0 and total > 0:
                    remove = max(0, temp_resist[roll[1].name] - total)
                    string += f" Reduced by {temp_resist[roll[1].name] - remove}"
                    dmg -= (temp_resist[roll[1].name] - remove)
                    temp_resist[roll[1].name] = remove
                string += " + "
                details += string 
            details = details[:-2]
        else:
            for roll in breakdown:
                print(roll)
                details += f"{'+'.join(map(str, roll[0]))} {roll[1].name} ({sum(roll[0])})"
        print(dmg)
        target['CurrentHp'] -= dmg
        details += f" {target['Name']} at {target['CurrentHp']} remaining"
        b = ""
        for roll in breakdown:
            b += f"{'+'.join(map(str, roll[0]))} ({sum(roll[0])}) {roll[1].name} + " 
        b = b[:-2]
        if 'Attack' in target:
            self.unit_breakdown.append(details)
            
            self.last_unit_dmg.append(f"Total Damage: {dmg} Breakdown: {b}")
        else:
            self.army_breakdown.append(details)
            self.last_army_dmg.append(f"Total Damage: {dmg} Breakdown: {b}")
        
        return target 


def main():
    sampletree = build_tree() 
    units = UnitTracker(sampletree)
    #for i in units.basis['Attack']['DamageRoll']['DamageType']['TYPE']: 
    #    print(i)
    pp(sampletree)
    print(sampletree['drow1']['Attack']())
    print(sampletree['drow2']['Attack']())
    print(sampletree['drowarmy1']['ArmyKills'](sampletree['drowarmy1']['ArmyKills']))
    print(units)
    print(sampletree['drow2']['Attack'].dict_object['DamageRoll'].to_file(4))
    print(sampletree['drow2']['Attack'].to_file(4))
    units.attack('drow2', 'drow1')
    units.attack('drow2', 'drow2')
    units.attack('drowarmy1', 'drowarmy1')
    with open('test.sfs', 'w') as fout:
        print(units.to_file(basis), file=fout)
    units2 = UnitTracker(build_tree('test.sfs'))
    print(units2)
    units.save(basis, 'SAMPLE.sfs')
    print(units.get_damage_type("Piercing"))
    print(units.basis["Attack"]['Button'])
    
    
if __name__ == "__main__":
    main()
