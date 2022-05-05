import LookBack_Apriori_Algorithm
import utilities
from flask import Flask, render_template,request
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

#Global variable, this allow to access data from all route 
sleep_value=0
temporal_window=0
min_support=0
min_confidence=0
filename=""
len_rules=0
rules=[]
onlyRules=[]
my_query=""
filter_t0=""
data=""
api=False


@app.route('/',methods=["POST","GET"])
def settingRules():
 # Take info from global variable
 global sleep_value
 global temporal_window
 global min_support
 global min_confidence
 global data
 global my_query
 global filterT0
 global api
 
 if request.method=="GET":
  api=False
  return render_template('settingRules.html') 

 #Read POST request from App API
 elif request.method=="POST":
  record=json.loads(request.data)
  data=record['data']
  sleep_value=record['sleep_value']
  temporal_window=record['temporal_window']
  min_confidence=record['min_confidence']
  min_support=record['min_support']
  my_query=record['my_query']
  filterT0=record['filterT0'] 
  api=True

  return rulesGeneration() 
 
@app.route('/rulesGeneration', methods=["POST","GET"])
def rulesGeneration(): 
 
 # Take info from global variable
 global sleep_value
 global temporal_window
 global min_support
 global min_confidence
 global filename
 global rules
 global onlyRules
 global data
 global api
 
 if request.method=="POST":
   #Take info from form if there isn't api request
  if not api:
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
     # take the dataset that contain my setting if it exist
     similarDataset=utilities.__rulesImplicitGeneration(data,sleep_value,temporal_window,min_support,min_confidence)
    
     #check if same setting already exist 
     if not utilities.__alreadySetting(filename) and similarDataset=="NULL":
      #RUN ALGORITHM (sorting is included)
      rules=LookBack_Apriori_Algorithm.run('Data/'+data,sleep_value,temporal_window,min_support,min_confidence)
      
      #save info in a file
      utilities.__saveSetting(rules,filename,temporal_window,sleep_value,min_support,min_confidence)
     
     #take info from file with exactly name [file with sam name already exist]
     elif similarDataset=="NULL":
         temporal_window,sleep_value,min_support,min_confidence,onlyRules,rules=utilities.__splitFile(filename)
     
     #take info from similar file
     elif similarDataset!="NULL":
         filename=similarDataset
         temporal_window,sleep_value,_,_,onlyRules,rules=utilities.__splitFile(filename)
         
         #take rule structure with specific confidence or support (not all rule)
         _,rules = utilities.__takeRuleImplicit(rules,min_support,min_confidence)
    
     if not api:
      return render_template("rulesGeneration.html", sleep_value=sleep_value,
      temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
      rules=rules,len_rules=len(rules))
     else: return matchQueryForm()
  
  # Error in form
  else:
      if not api:
       return render_template("settingRules.html",message=message)
      else: return json.dumps({'description':message,'typeMatch' : '', 'ruleMatch' :'' })
 
 #GET request
 elif request.method=="GET":
       return render_template("rulesGeneration.html", sleep_value=sleep_value,
       temporal_window=temporal_window,min_support=min_support,min_confidence=min_confidence,
       rules=rules,len_rules=len(rules))

@app.route('/matchQueryForm', methods=["POST","GET"])
def matchQueryForm():
 global api
 if not api:
  return render_template('matchQueryForm.html',temporal_window=temporal_window) 
 else: return matchingQuery()


@app.route('/matchingQuery', methods=["POST","GET"])
def matchingQuery():
    
    # Take info from global variable
    global temporal_window
    global min_support
    global min_confidence
    global onlyRules
    global rules
    global my_query
    global filterT0
    global api

    temporal_window=int(temporal_window)
    min_support=float(min_support)
    min_confidence=float(min_confidence)

    #obtain info from form
    if not api:
     my_query=request.form.get('my_query')
     filterT0=request.form.get('filterT0')
    
    #Check if form is uncompleted or query is invalid
    value,message = utilities.__isQueryValid(temporal_window,my_query)
    if not value:
        if not api:
         return render_template("matchQueryForm.html",message=message,temporal_window=temporal_window)
        else: return json.dumps({'description':message,'typeMatch' : '', 'ruleMatch' :'' })

    #take only rule with specific confidence or support not all rule
    onlyRules,_ = utilities.__takeRuleImplicit(rules,min_support,min_confidence)

    #MATCHING QUERY
    typeMatch, ruleMatch=utilities.__findMatching(my_query,onlyRules,filterT0)

    if not api:
     return render_template('matchingQuery.html',my_query=my_query, typeMatch=typeMatch, ruleMatch=ruleMatch) 
    else:
        result = {'description':'correct','typeMatch' : typeMatch, 'ruleMatch' : ruleMatch}
        return json.dumps(result)

