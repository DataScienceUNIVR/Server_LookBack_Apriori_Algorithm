#https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html
#https://github.com/macloo/python-adv-web-apps/tree/master/python_code_examples/flask/actors_app/templates

#Lista di tutti i form presenti
#https://github.com/macloo/python-adv-web-apps/blob/master/python_code_examples/flask/forms/WTForms-field-types.csv

#Ereditarietà jinja flask
#https://jinja.palletsprojects.com/en/3.0.x/templates/


from asyncore import write
from email.policy import default
from select import select
from tokenize import String
from wsgiref.validate import validator
import LookBack_Apriori_Algorithm
import utilities
import json
from flask import Flask, make_response, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from turtle import onclick, position
from tkinter import Tk, filedialog
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)


# all Flask routes below
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/algorithm', methods=["POST","GET"])
def algorithm():  
    data=request.form.get('data_select')
    sleep_value= request.form.get("sleep_value")
    temporal_window=request.form.get("temporal_window")
    min_support=request.form.get("min_support")
    min_confidence=request.form.get("min_confidence")

    correct=True
    
    #check if all value are present
    if data=="null" or not sleep_value or not temporal_window or not min_support or not min_confidence:
     correct=False
     message="All value required"
    else:
     sleep_value= int(sleep_value)
     temporal_window=int(temporal_window)
     min_support=float(min_support)
     min_confidence=float(min_confidence)

    #check range of value
    if correct:
     message,correct=utilities.__dataRange(sleep_value,temporal_window,min_support,min_confidence)
    
    if correct:
       #extend path C:/Users/Marco Castelli/Documents/PytonWorkspace/newproject/Data/pm1
       data='Data/'+data
       
       #run algorithm (sorting is included)
       rules,len_rules=LookBack_Apriori_Algorithm.run(data,sleep_value,temporal_window,min_support,min_confidence)
      
       #save info in a file
       utilities.__saveSetting(temporal_window,rules,'setting.txt')

       return render_template("algorithm.html", sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
       rules=rules,len_rules=len_rules)
    else:
        return render_template("index.html",message=message)

@app.route('/algorithm/matchQueryForm', methods=["POST","GET"])
def matchQueryForm():
    temporal_window,rules=utilities.__splitFile()
    return render_template('matchQueryForm.html',rules=rules,temporal_window=temporal_window) 

@app.route('/algorithm/matchQueryForm/matchingQuery', methods=["POST","GET"])
def matchingQuery():
    temporal_window,rules=utilities.__splitFile()

    #obtain info from form
    my_query=request.form.get('my_query')

    #Check if form is uncompleted
    if my_query == "":
        return render_template("matchQueryForm.html",message="Query empty",temporal_window=temporal_window)
    if temporal_window==2 and "t3" in my_query:
        return render_template("matchQueryForm.html",message="Temporal window is 2 so, you can't specify activity in t3",temporal_window=temporal_window)
    if temporal_window==1 and ("t3" in my_query or "t2" in my_query):
        return render_template("matchQueryForm.html",message="Temporal window is 1 so, you can specify activity only t1",temporal_window=temporal_window)


    typeMatch, ruleMatch=utilities.findMatching(my_query,rules)

    return render_template('matchingQuery.html',my_query=my_query, typeMatch=typeMatch, ruleMatch=ruleMatch) 

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)