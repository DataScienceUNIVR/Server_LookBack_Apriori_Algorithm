import utilities,LookBack_Apriori_Algorithm

temporal_window,_,_,_,rules,_=utilities.__splitFile()

my_query="LA_3_t3 + LA_3_t2 + MA_3_t1 + R_1_t1"  
#delete white space 
my_query=my_query.replace(" ","")
 
 #obtaing activity from query
query_activity=utilities.__splitActivity(my_query)

#print(utilities.__isSimilar(["HA_2_t2"],["HA_2_t2","MA_2_t2"]))

print(utilities.__findMatching(my_query,rules,"OFF"))
