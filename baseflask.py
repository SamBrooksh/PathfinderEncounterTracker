from flask import Flask, redirect, url_for, request, render_template
from fileloader import build_tree, UnitTracker
from keybuilder import load_keys
import os
from enum import EnumType
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

@app.route('/testing', methods=['GET', 'POST'])
def test():
    basis = load_keys()
    if request.method == 'POST':
        units = {}
        unit_id = 0
        print(request.form)
        for key in basis:
            
            print(f"{key} : {request.form.getlist(key)}")

        #print(request.form.getlist('Gear[]'))
    return render_template('new_encounter_guarantee.html', basis=basis)

if __name__ == '__main__':
    app.run(debug=True)