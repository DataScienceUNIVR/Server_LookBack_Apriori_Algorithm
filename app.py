import LookBack_Apriori_Algorithm
import utilities
from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
import os.path
app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

# all Flask routes below

@app.route('/', methods=["POST","GET"])
def matchQueryForm():
    #check if file with rule exist
    if os.path.exists("setting.txt"):
     temporal_window,_,_,_,rules,_=utilities.__splitFile()
     return render_template('matchQueryForm.html',rules=rules,temporal_window=temporal_window) 
    else: 
     return render_template('settingRules.html')

@app.route('/settingRules')
def settingRules():
    return render_template('settingRules.html')
 
@app.route('/rulesGeneration', methods=["POST","GET"])
def rulesGeneration():  
 if request.method=="POST":
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
     utilities.__saveSetting(sleep_value,temporal_window,min_support,min_confidence,rules)
 
     return render_template("rulesGeneration.html", sleep_value=sleep_value,
     temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
     rules=rules,len_rules=len_rules)
  else:
      return render_template("settingRules.html",message=message)
 
 elif request.method=="GET":
       temporal_window,sleep_value,min_support,min_confidence,_,rules=utilities.__splitFile()
       return render_template("rulesGeneration.html", sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
       rules=rules,len_rules=len(rules))

@app.route('/matchingQuery', methods=["POST","GET"])
def matchingQuery():
    temporal_window,_,_,_,rules,_=utilities.__splitFile()
    temporal_window=int(temporal_window)

    #obtain info from form
    my_query=request.form.get('my_query')
    filterT0=request.form.get('filterT0')
    
    #Check if form is uncompleted or query is invalid
    value,message = utilities.__isQueryValid(temporal_window,my_query)
    if not value:
        return render_template("matchQueryForm.html",message=message,temporal_window=temporal_window)

    typeMatch, ruleMatch=utilities.__findMatching(my_query,rules,filterT0)

    return render_template('matchingQuery.html',my_query=my_query, typeMatch=typeMatch, ruleMatch=ruleMatch) 

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)