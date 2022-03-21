from operator import itemgetter

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
     rule['completeness']=priority          #add  criteria into list
     rule['size']=len(rule['rule'][:rule['rule'].index('-')])        # add second criteria into a list

    return rules
  
