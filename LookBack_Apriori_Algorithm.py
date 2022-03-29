#Only code for temporal_apriori_algorithm with json
from audioop import reverse
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
from copy import copy
import utilities

class TemporalEvent:
    #A temporal event is identified by a name and a location in time from t0 to t-n.
    def __init__(self, name):
        self.name = name
        self.timeloc = 0

    def set_timeloc(self, timeloc):
        self.timeloc = timeloc

    def __repr__(self):
        return self.name + '_t' + str(self.timeloc)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name and self.timeloc == other.timeloc

    def __hash__(self):
        return hash((self.name, self.timeloc))

def classic_apriori(dataset, min_support=0.5):
    te = TransactionEncoder()
    transactions = te.fit(dataset).transform(dataset)
    df = pd.DataFrame(transactions, columns=te.columns_)
    return apriori(df, min_support=min_support, use_colnames=True)
def temporal_from_strings(dataset):
    new_dataset = []
    for i in range(len(dataset)):
        new_dataset.append([])
        for j in range(len(dataset[i])):
            if dataset[i][j] != '':
                new_dataset[i].append(TemporalEvent(dataset[i][j]))

    return new_dataset

def augment_by_column(dataset, temporal_window=None):
    #new version, starts by populating the last column (t0) and goes back.
    if temporal_window == None:
        temporal_window = len(dataset)
        print(temporal_window)

    augmented_dataset = []
    for i in range(len(dataset)):
        augmented_dataset.append(dataset[i])

    for j in range(temporal_window):
        for i in range(j+1, len(dataset)):
            augmented_row = []
            for el in dataset[i-(1+j)]:
                el_copy = copy(el)
                el_copy.set_timeloc(j+1)
                augmented_row.append(el_copy)

            augmented_dataset[i] = augmented_row + augmented_dataset[i]

    return augmented_dataset

def order_itemset(itemset):
    return sorted(itemset, key=lambda x: (-x.timeloc, x.name))

def find_sleep_patterns(frequent_itemsets, sleep_value=3, min_support=0, min_confidence=0):
    sleep_frequent_patterns = []
    frequent_itemsets_dict = {}
    count = 0
    for index, row in frequent_itemsets.iterrows():
        itemset = row['itemsets']
        support = row['support']
        ordered_itemset = order_itemset(itemset)

        key = ordered_itemset[0].__repr__()
        if len(ordered_itemset) > 1:
            key = ' + '.join([x.__repr__() for x in ordered_itemset])
        frequent_itemsets_dict[key] = support

        last_item = ordered_itemset[-1] #this assumes that SL is always gonna be the last item, but it is not accurate (sometimes it is ST), quick fix = change SL to ZL in the original dataset
        if len(ordered_itemset) > 1 and last_item.name == 'ZL_' + str(sleep_value) and last_item.timeloc == 0 and support >= min_support: # .startswith('SL_' + str(sleep_value)):
            count += 1
            sleep_frequent_patterns.append((support, ordered_itemset))

    return sleep_frequent_patterns, frequent_itemsets_dict

def find_sleep_rules(frequent_patterns, frequent_itemsets_dict, n_days, min_support=0, min_confidence=0):
    rules = []

    for support, frequent_pattern in frequent_patterns:
        antecedents = ' + '.join([x.__repr__() for x in frequent_pattern[:-1]])
        consequent = frequent_pattern[-1].__repr__()

        rule = antecedents + ' -> ' + consequent
        antecedents_support = frequent_itemsets_dict[antecedents.strip()]
        confidence = support/antecedents_support
        
        if confidence >= min_confidence:
            rules.append({'rule':rule, 'confidence':confidence,'support':support})

    return rules

def wrapper_function(dataset, sleep_value, temporal_window=0, min_support=0.2, min_confidence=0.5):
    temporal_dataset = temporal_from_strings(dataset)
    augmented_dataset = augment_by_column(temporal_dataset, temporal_window=temporal_window)
    frequent_itemsets = classic_apriori(augmented_dataset, min_support=min_support)
    sleep_frequent_patterns, frequent_itemsets_dict = find_sleep_patterns(frequent_itemsets, sleep_value=sleep_value, min_support=min_support)
    n_days = len(dataset)
    rules = find_sleep_rules(sleep_frequent_patterns, frequent_itemsets_dict, n_days, min_confidence=min_confidence)
    return rules

def print_rules(rules, min_support=0, min_confidence=0):
    confidence = 1
    support = 0.01
    max_support_rules = []
    for i in range(len(rules)):
        rule = rules[i]
        antecedent = rule['rule'].split('->')[0]
        if 'ZL' not in antecedent and rule['support'] >= min_support and rule['confidence'] >= min_confidence:
            print(i, ')', rule)

def get_latex_activity(consequent):
    activity, intensity, timestep = consequent.split('_')[0], consequent.split('_')[1], consequent.split('_')[2]
    if activity == ' ZL':
        activity = 'SL'
    return activity  + ':' + intensity
    

def get_latex_from_rule(rule):
    antecedent, consequent = rule.split(' -> ')[0], rule.split('->')[1]
    latex_rule = '$\{'
    antecedents = antecedent.split(' + ')
    timeloc = int(antecedents[0][-1])
    for i in range(len(antecedents)):
        antecedent = antecedents[i]
        new_timeloc = int(antecedent[-1])
        if new_timeloc != timeloc:
            latex_rule += '\}_{' + str(-int(timeloc)) + '} \wedge \{'
            timeloc = new_timeloc

        elif i != 0:
            latex_rule += ', '

        latex_rule += get_latex_activity(antecedent) 

    latex_rule += '\}_{' + str(-int(timeloc)) + '}'
    print(latex_rule)
    latex_rule = latex_rule + ' \\rightarrow \{' + get_latex_activity(consequent) + '\}_0$' #wtf is up with python and backslash??
    print(latex_rule)
    return latex_rule

"""#PMDATA JSON IMPORT"""

def run(path,sleep_value, temporal_window=2, min_support=0.02, min_confidence=0):
 light_activity_df = pd.read_json(path+'/lightly_active_minutes.json')
 moderate_activity_df = pd.read_json(path+'/moderately_active_minutes.json')
 heavy_activity_df = pd.read_json(path+'/very_active_minutes.json')  
 rest_df = pd.read_json(path+'/sedentary_minutes.json')
 sleep_quality_df = pd.read_json(path+'/sleep.json')
 sleep_quality_df = sleep_quality_df[['dateOfSleep', 'efficiency']]
 
 sleep_quality_df = pd.read_csv(path+'/sleep_score.csv')
 #crop date only
 sleep_quality_df['timestamp'] = sleep_quality_df['timestamp'].astype('datetime64').dt.date
 #timeshift back 1 day
 sleep_quality_df['timestamp'] = sleep_quality_df['timestamp'] - pd.Timedelta(days=1)
 
 sleep_quality_df['timestamp']
 
 sleep_quality_df = sleep_quality_df[['timestamp','overall_score']]
 
 light_activity_df.columns = ['date', 'light']
 moderate_activity_df.columns = ['date', 'moderate']
 heavy_activity_df.columns = ['date','heavy']
 rest_df.columns = ['date','rest']
 sleep_quality_df.columns = ['date','sleep']
 
 sleep_quality_df['date'] = sleep_quality_df['date'].astype('datetime64')
 
 sleep_and_activity_df = light_activity_df.merge(moderate_activity_df, on='date').merge(heavy_activity_df, on='date').merge(rest_df, on='date').merge(sleep_quality_df, on='date')
 
 """DISCRETIZATION"""
 
 sleep_and_activity_df['light_discretized'] = pd.qcut(sleep_and_activity_df['light'], q=3, labels=['LA_1','LA_2','LA_3'])
 sleep_and_activity_df['moderate_discretized'] = pd.qcut(sleep_and_activity_df['moderate'], q=3, labels=['MA_1','MA_2','MA_3'])
 sleep_and_activity_df['heavy_discretized'] = pd.qcut(sleep_and_activity_df['heavy'], q=3, labels=['HA_1','HA_2','HA_3'])
 sleep_and_activity_df['rest_discretized'] = pd.qcut(sleep_and_activity_df['rest'], q=3, labels=['R_1','R_2','R_3'])
 sleep_and_activity_df['sleep_discretized'] = pd.qcut(sleep_and_activity_df['sleep'], q=3, labels=['ZL_1','ZL_2','ZL_3'])
 
 #only problem now is values of 0 are considered (only in moderate and heavy activity)
 dataset = []
 for row in sleep_and_activity_df[['light_discretized', 'moderate_discretized','heavy_discretized','rest_discretized','sleep_discretized']].itertuples():
     dataset.append([str(row.light_discretized), str(row.moderate_discretized), str(row.heavy_discretized), str(row.rest_discretized), str(row.sleep_discretized)])
 
 """#EXPERIMENTS"""
 
 rules = wrapper_function(dataset, sleep_value, temporal_window, min_support, min_confidence)
 #sort rules
 rules=utilities.__rulesSorting(rules,temporal_window)

 return rules,len(rules) 