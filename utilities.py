from operator import itemgetter
import re
# function to return error message about form in index
def __dataRange(sleep_value,temporal_window,min_support,min_confidence):
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

# sorting rules from all rules
def rulesSorting(rules,temporal_window):
    __addCriteria(rules,temporal_window)
    rules = sorted(rules, key = itemgetter('support','completeness','size'),reverse=True)
    return rules

# add two new criteria into a list
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
  
# from a file return temporal window and a list of rules
def __splitFile():
    rules=""
    with open('setting.txt','r') as f:
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

#create a file_name file to save mining rules and temporal_window
def __saveSetting(sleep_value,temporal_window,min_support,min_confidence,rules):
 
 #obtain only the rule(the string)
 #only_rule=(x['rule'] for x in rules)
       
 #save information in a file
 with open('setting.txt','w') as f:
  f.write(str(temporal_window)+',')
  f.write(str(sleep_value)+',')
  f.write(str(min_support)+',')
  f.write(str(min_confidence)+'\n')
  for e in rules:
   f.write(e['rule']+','+str(e['confidence'])+','+str(e['support'])+','+str(e['completeness'])+','+str(e['size'])+'\n')

#from a rule return activity_t1, actvity_t2, activity_t3
def __splitActivity(rule):

    rule=rule.replace("+", ",")       #use this because split with + has a bug
    rule=re.split(',',rule)           #obtain a list of activity for a specific rule
    
    activity_t3=[]
    activity_t2=[]
    activity_t1=[]

    for activity in rule:
        if "t3" in activity:
            activity_t3.append(activity)
        elif "t2" in activity:
            activity_t2.append(activity)
        elif "t1" in activity:
            activity_t1.append(activity)
    
    return activity_t3,activity_t2,activity_t1

# check if two activity are similar if they have same type [HA_3_t2,MA_1_t2] and [HA_2_t2]
def __isSimilar(activity,query_activity):
  
  if not activity and not query_activity:
      return True
  #Delete the same
  r_query_activity=list(set(query_activity) - set(activity))
  r_activity=list(set(activity) - set(query_activity))

  for elemQuery in r_query_activity:
      deletable=True
      for elemActivity in r_activity:
         if  ("HA" in elemActivity and "HA" in elemQuery or
         "MA" in elemActivity and "MA" in elemQuery or
         "LA" in elemActivity and "LA" in elemQuery or
         "R" in elemActivity and "R" in elemQuery or
         "ZL" in elemActivity and "ZL" in elemQuery):
          deletable=False
      if(deletable):
        r_query_activity.remove(elemQuery) 
 
  #Something in common
  if len(r_query_activity)>0:
     return True

  return False   

#1) First criteria: EXACT MATCH
def __ExactMatch(my_query, rules,query_activity_t3,query_activity_t2,query_activity_t1):
 for rule in rules:
     rule_antecedent=rule[:rule.index('-')] #take only string before ->, so the antecedent
     rule_antecedent=rule_antecedent.replace(" ", "")       #delete all white space
     
     activity_t3,activity_t2,activity_t1=__splitActivity(rule_antecedent)

     if activity_t3==query_activity_t3 and activity_t2==query_activity_t2 and activity_t1==query_activity_t1:
      return "EXACT MATCH",rule
 return 'NULL','NULL'

#2) Second criteria: MATCH
def __Match(rules,query_activity_t3,query_activity_t2,query_activity_t1):
 for rule in rules:
     rule_antecedent=rule[:rule.index('-')] #take only string before, so the antecedent->
     rule_antecedent=rule_antecedent.replace(" ", "")       #delete all white space

    #Obtain activity for day in generated rules
     activity_t3,activity_t2,activity_t1=__splitActivity(rule_antecedent)

   #check if query rule (user) is a subset of rule generated from algorithm
     if set(activity_t3).issubset(query_activity_t3) and set(activity_t2).issubset(query_activity_t2) and set(activity_t1).issubset(query_activity_t1):
         return "MATCH",rule
 return 'NULL','NULL'

#3) Third criteria: PARTIAL MATCH
def __PartialMatch(rules,query_activity_t3,query_activity_t2,query_activity_t1):
 for rule in rules:
     rule_antecedent=rule[:rule.index('-')] #take only string before, so the antecedent->
     rule_antecedent=rule_antecedent.replace(" ", "")       #delete all white space

    #Obtain activity for day in generated rules
     activity_t3,activity_t2,activity_t1=__splitActivity(rule_antecedent)
     
     # Rule generated
     activity_not_similar=[]
     activity_possible_similar=[activity_t3,activity_t2,activity_t1]

     # Query rule
     query_not_similar=[]
     query_possible_similar=[query_activity_t3,query_activity_t2,query_activity_t1]

    #Not similar list means MATCH
     if set(activity_t3).issubset(query_activity_t3) and activity_t3 and query_activity_t3:
        activity_not_similar.append(activity_t3)
        query_not_similar.append(query_activity_t3)
     if set(activity_t2).issubset(query_activity_t2) and activity_t2 and query_activity_t2:
        activity_not_similar.append(activity_t2)
        query_not_similar.append(query_activity_t2)
     if set(activity_t1).issubset(query_activity_t1) and activity_t1 and query_activity_t1:
        activity_not_similar.append(activity_t1)
        query_not_similar.append(query_activity_t1)
    
    # List of possible similar
     activity_possible_similar=[item for item in activity_possible_similar if not item in activity_not_similar]
     query_possible_similar=[item for item in query_possible_similar if not item in query_not_similar]
   
    #Check if all activity in possible_similar is similar 
     similar=True
     for i in range(len(activity_possible_similar)):
         if(not __isSimilar(activity_possible_similar[i],query_possible_similar[i])):
             similar=False
     if(similar and len(activity_possible_similar)<3 and len(activity_not_similar)>0):
         return "PARTIAL MATCH",rule
     #All activity in t3,t2,t1 are similar
     elif similar:
      return "SIMILAR MATCH", rule
  
 return 'NULL','NULL'

#find matching betwenn user query and all rules generated by LookBack Apriori Algorithm
# return rule match
def findMatching(my_query, rules):
 #delete white space
 my_query=my_query.replace(" ","")
 
 #obtaing activity from query
 query_activity_t3,query_activity_t2,query_activity_t1=__splitActivity(my_query)

 #1) EXACT MATCH result
 message,rule=__ExactMatch(my_query, rules,query_activity_t3,query_activity_t2,query_activity_t1)
 if message!="NULL":
     return message,rule

 #2) MATCH result
 message,rule=__Match(rules,query_activity_t3,query_activity_t2,query_activity_t1)
 if message!="NULL":
     return message,rule
 
 #3) PARTIAL MATCH result
 message,rule=__PartialMatch(rules,query_activity_t3,query_activity_t2,query_activity_t1)
 if message!="NULL":
     return message,rule
     
 return "NO RULES FOUND", "NULL"
   