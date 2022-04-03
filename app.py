from fileinput import filename

from sklearn.impute import SimpleImputer
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


#global variable
sleep_value=0
temporal_window=0
min_support=0
min_confidence=0
filename=""
len_rules=0


@app.route('/')
def settingRules():
    return render_template('settingRules.html')
 
@app.route('/rulesGeneration', methods=["POST","GET"])
def rulesGeneration(): 

 global sleep_value
 global temporal_window
 global min_support
 global min_confidence
 global filename
 
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
  
   filename= "{data},{sleep_value},{temporal_window},{min_support},{min_confidence}".format(
       data=data,sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,
       min_confidence=min_confidence)

  if correct:
     data='Data/'+data
     # take the dataset that contain my setting if it exist
     similarDataset=utilities.__rulesImplicitGeneration(data,sleep_value,temporal_window,min_support,min_confidence)
     #check if same setting already exist 
     if not utilities.__alreadySetting(filename) and similarDataset=="NULL":
      #run algorithm (sorting is included)
      rules,len_rules=LookBack_Apriori_Algorithm.run(data,sleep_value,temporal_window,min_support,min_confidence)
      #save info in a file
      utilities.__saveSetting(rules,filename,temporal_window,sleep_value,min_support,min_confidence)
     
     #take info from file with exactly name
     elif similarDataset=="NULL":
         temporal_window,sleep_value,min_support,min_confidence,_,rules=utilities.__splitFile(filename)
     
     #similar file
     elif similarDataset!="NULL":
         filename=similarDataset
         temporal_window,sleep_value,_,_,_,rules=utilities.__splitFile(filename)
         
         #take only rule with specific confidence or support not all rule
         res=[]
         for rule in rules:
             if float(rule['support']) >= min_support and float(rule['confidence']) >= min_confidence:
                 res.append(rule)
         rules=res
     
     
     return render_template("rulesGeneration.html", sleep_value=sleep_value,
     temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
     rules=rules,len_rules=len(rules))
  else:
      return render_template("settingRules.html",message=message)
 
 elif request.method=="GET":
       temporal_window,sleep_value,min_support,min_confidence,_,rules=utilities.__splitFile(filename)
       return render_template("rulesGeneration.html", sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
       rules=rules,len_rules=len(rules))

@app.route('/matchQueryForm', methods=["POST","GET"])
def matchQueryForm():
     return render_template('matchQueryForm.html',temporal_window=temporal_window) 


@app.route('/matchingQuery', methods=["POST","GET"])
def matchingQuery():
    global temporal_window
    _,_,_,_,onlyrules,rules=utilities.__splitFile(filename)
    temporal_window=int(temporal_window)
    
    #take only rule with specific confidence or support not all rule
    res=[]
    for rule in rules:
     if float(rule['support']) >= min_support and float(rule['confidence']) >= min_confidence:
      res.append(rule)
      rules=res

    onlyRules = [ sub['rule'] for sub in rules ]
    #obtain info from form
    my_query=request.form.get('my_query')
    filterT0=request.form.get('filterT0')
    
    #Check if form is uncompleted or query is invalid
    value,message = utilities.__isQueryValid(temporal_window,my_query)
    if not value:
        return render_template("matchQueryForm.html",message=message,temporal_window=temporal_window)

    typeMatch, ruleMatch=utilities.__findMatching(my_query,onlyRules,filterT0)

    return render_template('matchingQuery.html',my_query=my_query, typeMatch=typeMatch, ruleMatch=ruleMatch) 

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)