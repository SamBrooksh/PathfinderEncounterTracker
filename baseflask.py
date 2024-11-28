from flask import Flask, redirect, url_for, request, render_template
from fileloader import build_tree, UnitTracker
app = Flask(__name__)

@app.route('/<file_name>')
def file(file_name):
    units = UnitTracker(build_tree(file_name+'.txt'))
    return render_template("units.html", units=units)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)