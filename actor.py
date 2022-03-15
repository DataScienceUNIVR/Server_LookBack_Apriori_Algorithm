#https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html
#https://github.com/macloo/python-adv-web-apps/tree/master/python_code_examples/flask/actors_app/templates

#Lista di tutti i form presenti
#https://github.com/macloo/python-adv-web-apps/blob/master/python_code_examples/flask/forms/WTForms-field-types.csv

#Ereditarietà jinja flask
#https://jinja.palletsprojects.com/en/3.0.x/templates/


from select import select
from tokenize import String
from wsgiref.validate import validator
import alg_cleaned,func
import string
from time import sleep
from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField,FloatField,FileField,RadioField
from wtforms.validators import DataRequired
from data import ACTORS
from modules import get_names, get_actor, get_id
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
class NameForm(FlaskForm):
    #1, temporal_window=2, min_support=0.02, min_confidence=0
    path=RadioField("Selectdirectory",validators=[DataRequired()],choices = ['pm1', 'pm2','pm3','pm4','pm5','pm6','pm7','pm8','pm9','pm10'])
    sleep_value=IntegerField("Sleep value",validators=[DataRequired()])
    temporal_window=IntegerField("Temporal window value",  validators=[DataRequired()])
    min_support=FloatField("Min support",validators=[DataRequired()])
    min_confidence=FloatField("Min confidence",validators=[DataRequired()])
    submit = SubmitField('Run Algorithm!')


# all Flask routes below
# aggiungiamo i metodi per gestire i dati dei form 
@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message=""
    #path=func.savePath()
    # restituisce true se il modulo è stato completato e inviato
    
    if form.validate_on_submit():
        #ottengo i dati presenti nei form
        path=form.path.data
        sleep_value=form.sleep_value.data
        temporal_window=form.temporal_window.data
        min_support=form.min_support.data
        min_confidence=form.min_confidence.data
    
        message,correct=dataRange(sleep_value,temporal_window,min_support,min_confidence)
        if correct==True:
         # invio i dati 
         if request.method == 'POST':
          #call algorithm
          #extend path C:/Users/Marco Castelli/Documents/PytonWorkspace/newproject/Data/pm1
          path='Data/'+path
          rules,len_rules=alg_cleaned.run(path,sleep_value,temporal_window,min_support,min_confidence)
          return render_template("algorithm.html",sleep_value = sleep_value, temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence, rules=rules,len_rules=len_rules)

    return render_template('index.html', form=form,message=message)

def dataRange(sleep_value,temporal_window,min_support,min_confidence):
    error=""
    correct=True

    if(sleep_value<1 or sleep_value> 3):
     error= "sleep_value correct range in [1,3]\n"
    if(temporal_window<1 or temporal_window> 3):
     error= error+"temporal_window correct range in [1,3]\n"
    if(min_support>1 or min_support<=0):
     error=error+"min_support correct range in (0,1]\n"
    if(min_confidence<=0 or min_confidence> 1):
     error=error+"min_confidence correct range in (0,1]\n"
    
    if(error!=""):
        correct=False

    return error,correct


# 2 routes to handle errors - they have templates too
"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500"""


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)