from flask import Flask, redirect, url_for, request, render_template, jsonify
from fileloader import build_tree, UnitTracker
from keybuilder import load_keys
import os
from copy import deepcopy
from enum import EnumType
from pprint import pprint
app = Flask(__name__)

def is_enum(obj):
    #print(f"{obj} : {isinstance(obj, EnumType)} : {type(obj)}")
    return isinstance(obj, EnumType)

app.jinja_env.filters['is_enum'] = is_enum

@app.route('/file/<file_name>', methods=['GET', 'POST'])    
def file(file_name):
    if '.sfs' not in file_name:
        units = UnitTracker(build_tree(file_name+'.sfs'))#Sam File Structure - just txt
    else:
        units = UnitTracker(build_tree(file_name))

    if request.method == 'GET':
        #print('In Get')
        return render_template("units.html", units=units)
    elif 'modify_amount' in request.form:
        #print('In Modify Amount')
        if request.form['name'] in units.units:
            damage = int(request.form['modify_amount'])
            damage_type = request.form['type'] 
            units.deal_unit_damage(units.units[request.form['name']], [([damage], units.get_damage_type(damage_type.split('.')[1]))], damage, "BROWSER")
        else:
            units.army_units[request.form['name']]["CurrentHp"] -= int(request.form['modify_amount'])
        if '.sfs' in file_name:
            units.save(units.basis, file_name)
        else:
            units.save(units.basis, file_name+'.sfs')
        return render_template("units.html", units = units)
    elif 'Callable' in request.form:
        print('Callable')
        unit_name = request.form['name']
        object_name = request.form['CallObject']
        #print(unit_name, object_name)
        result = units.units[unit_name][object_name]()
        print(result)
        return render_template("result.html", units = units, result = result)

@app.route('/new_encounter', methods=['POST', 'GET'])
def new_encounter():
    if request.method == 'GET':
        return render_template('new_encounter.html', basis=load_keys())
    else:
        print("Create and Save")
        print(request.form['value'])
        return render_template('new_encounter.html', basis=load_keys())

@app.route('/')
def index():
    local_files = os.listdir()
    encounters = []
    for file in local_files:
        if ".sfs" in file:
            encounters.append(file)
    return render_template('index.html', files = encounters)

@app.route('/redirect', methods=['POST', 'GET'])
def go_to_file():
    error = None
    if request.method == 'GET':
        print(request.form)
    return '/'

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    print(data)
    return jsonify({'data' : data})

def build_units(validating:dict)->dict:
    units = {}
    for key in validating:
        new_unit = key.split(':')
        if new_unit[0] not in units:
            units[new_unit[0]] = {}
        if '-' in new_unit[1]:
            
            sub_key = new_unit[1].split('-')
            if len(sub_key) > 2:
                if sub_key[-1] != "":
                    units[new_unit[0]][sub_key[0]][sub_key[1]] =  {sub_key[2] : validating[key]}
            else:
                if sub_key[0] not in units[new_unit[0]]:
                    units[new_unit[0]][sub_key[0]] = {}
                units[new_unit[0]][sub_key[0]][sub_key[1]] = validating[key]
        else:
            units[new_unit[0]][new_unit[1]] = validating[key]

    return units

def validate_dict(basis: dict, validating: dict)->tuple[bool, str]:
    #Returns any errors, and if it is successful
    removes = []
    for key in validating:
        if '[]' in key:
            removes.append(key)
    to_save = validating.pop('file')
    #if os.path.exists(to_save+".sfs"):
    #    return False, "ENCOUNTER EXISTS ALREADY"
    for i in removes:
        validating.pop(i)
    #READY TO CHECK
    errors = []
    built = build_units(validating)
    pprint(built)
    with open(to_save+".sfs", 'w') as fout:
        spacing = 0
        for key in built:
            print(f"{key}:", file=fout)
            spacing += 4
            for sub_key in built[key]:
                try:
                    if isinstance(built[key][sub_key], dict):
                        print(f"{any(built[key][sub_key].values())}: {sub_key} : {built[key][sub_key]}")
                        if any(built[key][sub_key].values()):
                            print(f"{" "*spacing}{sub_key}:", file=fout)
                            spacing += 4
                            for sub_sub_key in built[key][sub_key]:
                                if isinstance(built[key][sub_key][sub_sub_key], dict):
                                    if any(built[key][sub_key][sub_sub_key].values()):
                                        print(f"{" "*spacing}{sub_sub_key}:", file=fout)
                                        spacing += 4
                                        for tertiary in built[key][sub_key][sub_sub_key]:
                                            print(f"{" "*spacing}{tertiary}:{built[key][sub_key][sub_sub_key][tertiary]}", file=fout)
                                        spacing -= 4
                                elif built[key][sub_key][sub_sub_key] == "":
                                    pass
                                else:
                                    print(f"{" "*spacing}{sub_sub_key}:{built[key][sub_key][sub_sub_key]}", file=fout)
                            spacing -= 4
                        else:
                            print(f"Skipped {sub_key}")
                    else:
                        if built[key][sub_key] != "":
                            print(f"{" "*spacing}{sub_key}:{built[key][sub_key]}", file=fout)
                except:
                    print("CRASH")
                    pass
    try:
        result = build_tree(to_save+".sfs")
    except Exception as e:
        print(e)
    return False, str(errors)

@app.route('/testing', methods=['GET', 'POST'])
def test():
    basis = load_keys()
    if request.method == 'POST':
        error = "TEST ERROR"
        units = {}
        #print(request.form) 
        for key in basis:
            if basis[key]['TYPE'] == "List":
                for item in request.form:
                    if key in item:
                        get_list = request.form.getlist(item)
                        units[item[:-2]] = get_list
                        units[item] = get_list
        for key in request.form:
            if key not in units:
                units[key] = request.form[key]
        # Data Validate
        valid, error = validate_dict(basis, deepcopy(units))


        return render_template('new_encounter_guarantee.html', basis=basis, data=units, error=error)

        #print(request.form.getlist('Gear[]'))
    return render_template('new_encounter_guarantee.html', basis=basis, data=None, error="")

if __name__ == '__main__':
    app.run(debug=True)