#https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html
#https://github.com/macloo/python-adv-web-apps/tree/master/python_code_examples/flask/actors_app/templates

#Lista di tutti i form presenti
#https://github.com/macloo/python-adv-web-apps/blob/master/python_code_examples/flask/forms/WTForms-field-types.csv

#Ereditarietà jinja flask
#https://jinja.palletsprojects.com/en/3.0.x/templates/


from select import select
from tokenize import String
from wsgiref.validate import validator
import LookBack_Apriori_Algorithm
import string
from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from turtle import onclick, position
from tkinter import Tk, filedialog

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

# with Flask-WTF, each web form is represented by a class
# "NameForm" the name of form can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
# questo modulo ha un solo campo di inserimento testo e uno di invio
# se volessi costruire più form li devo definire in una nuova classe
# DataRequired fa si che i form non siano vuoti


# all Flask routes below
# aggiungiamo i metodi per gestire i dati dei form 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/algorithm', methods=["POST"])
def algorithm():  
    data=request.form.get('data_select')
    sleep_value= request.form.get("sleep_value")
    temporal_window=request.form.get("temporal_window")
    min_support=request.form.get("min_support")
    min_confidence=request.form.get("min_confidence")

    correct=True

    #check if all value are present
    if not data or not sleep_value or not temporal_window or not min_support or not min_confidence:
     correct=False
     message="All value required"
    else:
     sleep_value= int(sleep_value)
     temporal_window=int(temporal_window)
     min_support=float(min_support)
     min_confidence=float(min_confidence)

    #check range of value
    if correct:
     message,correct=dataRange(sleep_value,temporal_window,min_support,min_confidence)
    
    if correct:
       #call algorithm
       #extend path C:/Users/Marco Castelli/Documents/PytonWorkspace/newproject/Data/pm1
       path='Data/'+data
       rules,len_rules=LookBack_Apriori_Algorithm.run(path,sleep_value,temporal_window,min_support,min_confidence)
       return render_template("algorithm.html", sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
       rules=rules,len_rules=len_rules)
    else:
        return render_template("index.html",message=message)

def dataRange(sleep_value,temporal_window,min_support,min_confidence):
    error=""
    correct=True

    if(sleep_value<1 or sleep_value> 3):
     error= "sleep_value correct range in [1,3];\n"
    if(temporal_window<1 or temporal_window> 3):
     error= error+"temporal_window correct range in [1,3];\n"
    if(min_support>1 or min_support<=0):
     error=error+"min_support correct range in (0,1];\n"
    if(min_confidence<=0 or min_confidence> 1):
     error=error+"min_confidence correct range in (0,1];\n"
    
    if(error!=""):
        correct=False

    return error,correct

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)