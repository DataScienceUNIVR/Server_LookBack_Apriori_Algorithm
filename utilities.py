from argparse import Action
from dataclasses import field
from operator import itemgetter
import re
import os.path
from os import walk

# ---- CHECK FUNCTION ----

# function to return error message about form in index
def __dataRange(sleep_value,temporal_window,min_support,min_confidence):
    error=""
    correct=True

    if(sleep_value<1 or sleep_value> 3):
     error= "sleep_value must be in [1,3];\n"
    if(temporal_window<1):
     error= error+"temporal_window must be in [1,+inf];\n"
    if(min_support>1 or min_support<=0):
     error=error+"min_support must be in (0,1];\n"
    if(min_confidence<=0 or min_confidence> 1):
     error=error+"min_confidence must be in (0,1];\n"
    
    if(error!=""):
        correct=False

    return error,correct

#Check is a query is valid so it has not activity in a malformed time or in a time > temporal_window
def __isQueryValid(temporal_window,my_query):
       
    #delete white space
    my_query=my_query.replace(" ","")
    
    if len(my_query)==0:
        return False,"Empty query!"
    
    #use this because split with + has a bug
    my_query=my_query.replace("+", ",")       

    activity=my_query.split(',')

    for elem in activity:
        if "HA" not in elem and "MA" not in elem and "LA" not in elem and "R" not in elem and "ZL" not in elem:
          return False,"Query has not valid activity!"
        index=elem.find('t')
        if index == -1:
            return False,"Query malformed!"
        else:
            if len(elem)-1==index:
                return False,"Query malformed!"
            if not elem[index+1:].isdigit():
                return False,"Activity specificy in temporal window malformed!"
            temp=int(elem[index+1:])
            if temp>temporal_window:
                return False,"Query has activity in: " + str(temp) + " but the temporal_window is: " + str(temporal_window) +"!"

    return True,"Query correct!"


# ----UTILITIES FUNCTION -----

# sorting rules from all rules
def __rulesSorting(rules,temporal_window):
    __addCriteria(rules,temporal_window)
    rules = sorted(rules, key = itemgetter('support','completeness','size'),reverse=True)
    return rules

# add two new criteria into a list, it's used to add completeness and size into all rule in rules
def __addCriteria(rules,temporal_window):
    for rule in rules:
     priority=0
     for i in range(temporal_window+1):      #[0 .. tem_win]
         if(rule['rule'][:rule['rule'].index('-')].find(("t"+str(i)))!=-1):      #find a if t0, t1,t2, .. (before ->) is in rule
             priority+=1
         else:
            priority-=0.5                   # this is a hole
     rule['completeness']=priority          #add  criteria into list
     rule['size']=len(rule['rule'][:rule['rule'].index('-')])        # add second criteria into a list

    return rules
  
# from a file return setting and a list of rules
def __splitFile(filename):
    rules=""
    with open('Setting/'+filename,'r') as f:
        res=f.read()

    temporal_window,sleep_value,min_support,min_confidence=list((res[:res.index('\n')]).split(','))
    rules=res[res.index('\n')+1:]  #obtain rules as one string
    rules = list(rules.split("\n")) #create a list of rules
    rules.pop() #delete last element is a \n
 
    res={}
    #List with rules with all value
    mylistRules = list()
    #Create a list of dictionary
    for rule in rules:
        a=rule[:rule.index(',')]
        b,c,d,e=rule[rule.index(',')+1:].split(',')
        res['rule']=a
        res['confidence']=b
        res['support']=c
        res['completeness']=d
        res['size']=e
        mylistRules.append(res)
        res={}
    
    #take only rules
    onlyRules = [ sub['rule'] for sub in mylistRules ]
    
    return temporal_window,sleep_value,min_support,min_confidence,onlyRules,mylistRules

#check if the setting already exist in a setting file
def __alreadySetting(filename):
 return os.path.exists('Setting/'+filename)

#check if a set of rules is implicit generation from another set of rule (file existing) [EX: min_confidence=0.2 containg min_conf=0.4,0.6,0.8,0.1 or support]
def __rulesImplicitGeneration(data,sleep_value,temporal_window,min_support,min_confidence):
 filenames = next(walk('Setting/'), (None, None, []))[2]
 for file in filenames:
     info=re.split(',',file)
     if info[0]==data and int(info[1])==sleep_value and int(info[2])==temporal_window and float(info[3]) <=min_support and float(info[4])<=min_confidence:
      return file
 return "NULL"

#create a file_name file to save mining rules and setting
def __saveSetting(rules,filename,temporal_window,sleep_value,min_support,min_confidence):
 
 #obtain only the rule(the string)
 #only_rule=(x['rule'] for x in rules)
       
 #save information in a file
 with open('Setting/'+filename,'w') as f:
  f.write(str(temporal_window)+',')
  f.write(str(sleep_value)+',')
  f.write(str(min_support)+',')
  f.write(str(min_confidence)+'\n')
  for e in rules:
   f.write(e['rule']+','+str(e['confidence'])+','+str(e['support'])+','+str(e['completeness'])+','+str(e['size'])+'\n')

#from a rule return activity in order t0,t1,t2,...
def __splitActivity(rule):

    rule=rule.replace("+", ",")       #use this because split with + has a bug
    rule=re.split(',',rule)           #obtain a list of activity for a specific rule
    
    result=[]
    indexMax=0
    
    #Find max temporal window with activity
    for activity in rule:
     if indexMax< int(activity[activity.find('t')+1:]):
         indexMax=int(activity[activity.find('t')+1:])
    
    #Create empty list
    for i in range(indexMax+1):
        result.append([])
    
    #Popolate result with activity
    for activity in rule:
     result[int(activity[activity.find('t')+1:])].append(activity)
    
    #result has this form: [[], [' MA_1_t1'], [' R_3_t2 '], ['HA_1_t3 ', ' MA_1_t3 ']]
    return result

#take the antecedent in a rule
def __ruleAntecedent(rule):
     #take only string before ->, so the antecedent
    rule_antecedent=rule[:rule.index('-')]
    #delete all white space
    rule_antecedent=rule_antecedent.replace(" ", "")  
    return rule_antecedent

#Return a new set of rule from rules with all rule with min_support and min_confidence
def __takeRuleImplicit(rules,min_support,min_confidence):
    res=[]
    for rule in rules:
     if float(rule['support']) >= min_support and float(rule['confidence']) >= min_confidence:
      res.append(rule)
      rules=res

    onlyRules = [ sub['rule'] for sub in rules ]
    return onlyRules,rules


# ----- MATCHING FUNCTION -----

# check if two activity are similar if they have same type [HA_3_t2,MA_1_t2] and [HA_2_t2]
def __isSimilar(activity,query_activity):
  
  #Empty rules are obviosly similar
  if activity==[] and query_activity==[]:
      return "Similar"
  #But same rules are not similar because their are equal (similar only rule with same activity but different value)
  if activity==query_activity:
      return "Partial"

  if len(activity)>len(query_activity):
   return "False"

  #Delete the same
  r_query_activity=list(set(query_activity) - set(activity))
  r_activity=list(set(activity) - set(query_activity))
  result=r_query_activity[:]

  #Find if for every element in my query there's something similar in matching rule
  for elemQuery in r_query_activity:
      nothingSimilar=True
      for elemActivity in r_activity:
         if  ("HA" in elemActivity and "HA" in elemQuery or
         "MA" in elemActivity and "MA" in elemQuery or
         "LA" in elemActivity and "LA" in elemQuery or
         "R" in elemActivity and "R" in elemQuery or
         "ZL" in elemActivity and "ZL" in elemQuery):
          nothingSimilar=False
      if(nothingSimilar):
        return "False"
 
  #Something in common or all equal
  return "Similar"   

#1) First criteria: EXACT MATCH
def __ExactMatch(rules,query_activity):
 for rule in rules:
     rule_antecedent=__ruleAntecedent(rule)
     activity=__splitActivity(rule_antecedent)
     
     #in my query there isn't activity in t0, so i put the same activity to facilate equality
     query_activity[0]=activity[0]
     if activity==query_activity:
      return "EXACT MATCH",rule
 return 'NULL','NULL'

#2) Second criteria: MATCH
def __Match(rules,query_activity):
 for rule in rules:
     rule_antecedent=__ruleAntecedent(rule)

     #Obtain activity for day in generated rules
     activity=__splitActivity(rule_antecedent)
     query_activity[0]=activity[0]
 
     #Find the index when activity are not null
     activityIndexNotNull = list(filter(lambda x: activity[x] != [], range(len(activity))))
     query_activityIndexNotNull = list(filter(lambda x: query_activity[x] != [], range(len(query_activity))))

    #Two rules must be the same temporal window and have activity in same time
     if(len(activity)==len(query_activity) and activityIndexNotNull==query_activityIndexNotNull):
      subset=True
      for i in range(len(activity)) :
         if(not set(activity[i]).issubset(query_activity[i]) and activity[i]):
             subset= False
      if subset:  
       return "MATCH",rule
 return 'NULL','NULL'     

#3) Third criteria: PARTIAL MATCH
def __PartialMatch(rules,query_activity):
 for rule in rules:
     rule_antecedent=__ruleAntecedent(rule)

     #Obtain activity for day in generated rules
     activity=__splitActivity(rule_antecedent)
     
     #in my query there isn't activity in t0, so i put the same activity to facilate equality
     query_activity[0]=activity[0]
     
     #Find the index when activity are not null
     activityIndexNotNull = list(filter(lambda x: activity[x] != [], range(len(activity))))
     query_activityIndexNotNull = list(filter(lambda x: query_activity[x] != [], range(len(query_activity))))

     #Two rules must be the same temporal window activity and have activity in same time
     if (len(activity)!=len(query_activity) or activityIndexNotNull!=query_activityIndexNotNull):
         continue

     #Save similarity of all activity 
     resultSimilar=[]
     for i in range(1,len(activity)):
      resultSimilar.append(__isSimilar(activity[i],query_activity[i]))

     #Some similar and some equal but at least one Partial
     if(all(x == 'Similar' or x=='Partial' for x in resultSimilar) and 'Partial' in resultSimilar):
      return "PARTIAL MATCH", rule
  
 return 'NULL','NULL'

#4) Fourth criteria: SIMILAR MATCH
def __SimilarMatch(rules,query_activity):
 for rule in rules:
     rule_antecedent=__ruleAntecedent(rule)

     #Obtain activity for day in generated rules
     activity=__splitActivity(rule_antecedent)
     
     #in my query there isn't activity in t0, so i put the same activity to facilate equality
     query_activity[0]=activity[0]
     
     #Find the index when activity are not null
     activityIndexNotNull = list(filter(lambda x: activity[x] != [], range(len(activity))))
     query_activityIndexNotNull = list(filter(lambda x: query_activity[x] != [], range(len(query_activity))))

     #Two rules must be the same temporal window activity and have activity in same time
     if (len(activity)!=len(query_activity) or activityIndexNotNull!=query_activityIndexNotNull):
         continue

     #Save similarity of all activity 
     resultSimilar=[]
     for i in range(1,len(activity)):
      resultSimilar.append(__isSimilar(activity[i],query_activity[i]))
     
     #All similar
     if(all(x == 'Similar' for x in resultSimilar)):
      return "SIMILAR MATCH", rule
  
 return 'NULL','NULL'

#find matching betwenn user query and all rules generated by LookBack Apriori Algorithm
# return rule match
def __findMatching(my_query, rules,filterT0):
 
 #delete white space
 my_query=my_query.replace(" ","")
 
 #obtaing activity from query
 query_activity=__splitActivity(my_query)

 #Take only rule with t0 in antecedent
 if filterT0=="on":
  rules = list(filter(lambda rule: "t0" in __ruleAntecedent(rule),rules))

 #1) EXACT MATCH result
 message,rule=__ExactMatch(rules,query_activity)
 if message!="NULL":
     return message,rule

 #2) MATCH result
 message,rule=__Match(rules,query_activity)
 if message!="NULL":
     return message,rule
 
 #3) PARTIAL MATCH result
 message,rule=__PartialMatch(rules,query_activity)
 if message!="NULL":
     return message,rule

 #4) SIMILAR MATCH result
 message,rule=__SimilarMatch(rules,query_activity)
 if message!="NULL":
     return message,rule

 return "NO RULES FOUND", "NULL"
   