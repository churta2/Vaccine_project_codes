import networkx as nx
import pandas as pd
from gurobipy import *
import time
import pickle
import copy
from multiprocessing import Pool
import os
import multiprocessing

path="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/Optimization_model"
os.chdir(path)

start = time.time()


graph_collection={}
reach_collection={}



node_list=[(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,4),(1,2),(1,3),(2,0),(2,1),(2,2)]
#node_list=pd.read_pickle('set_nodes.pkl')


single_spread=pd.read_pickle('single_spread.pkl')


#########################################################

# Generating data for warm up

##=========================NUMBER OF SCENARIOS==================


##====I could improve this line with set operations/load graphs inside

single_spread = {}
escenarios=4  ####================== Number of scenarios

#escenarios=33


dict_reach={}

nodes_set=set(node_list)

for j in range(escenarios):
    
     #name="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/Optimization_model/copy_final_graphs/graph_"+str(j)+".pkl"
     name="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/Optimization_model/graph_"+str(j)+".pickle"
     file = open(name,'rb')
     G = pickle.load(file)
     graph_collection[j]=G
     print('Loop1')
     
     cascade_nodes_set=set(list(G.nodes()))
     cascade_nodes_list=list(G.nodes())
     
     temp_set=copy.deepcopy(nodes_set)
     not_in_cascade=temp_set.difference(cascade_nodes_set)
     
     for i in cascade_nodes_list:
        print('Loop2')
        temp_key = (i, j)
        T = nx.bfs_tree(G, source=i)
        reach_collection[temp_key]=set(list(T.nodes))
        reach_0 = len(list(T.nodes))
        single_spread[temp_key] = reach_0
    
   
     for i in list(not_in_cascade):
        print('Loop3')
        temp_key = (i, j)
        single_spread[temp_key] = 1
        reach_collection[temp_key]={i}



with open('reach_collection.pkl', 'wb') as f:
    pickle.dump(reach_collection, f)

with open('single_spread.pkl', 'wb') as f:
    pickle.dump(single_spread, f)

#####Calculating the spread==================================================





############### ======Optimization model======================================

###==== build the groups 

#test= pd.read_pickle("C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/Optimization_model/graphs_both/graphs_future/graph_903.pkl")



I=pd.read_pickle('set_I.pkl')
O=pd.read_pickle('set_O.pkl')

# I=[0,1,2]
# O=[[0,1,2,3],[0,1,2,3,4],[0,1,2]]

W = escenarios  # Number of escenarios
n = len(node_list)
number_batches=180
size_batch=1000

# number_batches=180
# size_batch=1000

big_m=1000000

# Building the model

m = Model("Influence")


m.Params.MIPFocus = 1
# Adding constraints and variables

node = m.addVars(node_list, vtype=GRB.BINARY, name="node")
theta_w = m.addVars(range(W), ub=n, vtype=GRB.CONTINUOUS, name="theta_w")

var_groups=m.addVars(I, vtype=GRB.INTEGER, name="groups")
excess=m.addVars(I, vtype=GRB.INTEGER, name="excess")
recep=m.addVars(I, vtype=GRB.INTEGER, name="recep")



 
for i in I:

    m.addConstr(sum(node[i,j] for j in O[i])-size_batch*(var_groups[i]) -recep[i]+ excess[i]== 0)  ### 
    m.addConstr(excess[i]<= size_batch*var_groups[i]*big_m)

m.addConstr(sum(var_groups[i] for i in I) == number_batches)
m.addConstr(sum(excess[i] for i in I) ==sum(recep[i] for i in I) )

cap = m.addConstr(sum(node[i] for i in node_list) == number_batches*size_batch)

###Adding warm-up constraint


for j in range(escenarios):
    warm = m.addConstr(theta_w[j] - sum(node[i] * single_spread[i, j] for i in node_list) <= 0)

# Adding objetive function

m.setObjective((1/W)*sum(theta_w[i] for i in range(W))- sum(excess[i] for i in I) - sum(recep[i] for i in I), GRB.MAXIMIZE)

m.optimize()



######check conditions to add cut

phaseI = m.getVars()
set_nodes = set(node_list)



######## CHECK THIS METHOD

def check_optimality(escenario,x_sol):


    A = set()

    for i in x_sol:
        A = A.union(reach_collection[node_list[i],escenario])

    sigma_w = len(A)
    set_not_reached=nodes_set.difference(A)
    not_reached=list(set_not_reached)
    
    
    
    if (sigma_w < phaseI[len(node_list) + escenario].x):
                        
        #print("=====ADDING_CUT_================")
        
        m.addConstr(theta_w[escenario]<= sigma_w+ sum(len(reach_collection[i,escenario].difference(A))*node[i] for i in not_reached))

        
        return sigma_w
    else:
        
        return sigma_w



def re_optimize():
    m.update()
    m.optimize()
    phaseI = m.getVars()
    #m.printAttr('X')
    return phaseI





phaseI=m.getVars()


iter=1
epsilon=2

UB=0
for i in range(len(node), len(node)+ len(theta_w)):
    UB+=(phaseI[i].x)/(W)

LB=0
escenarios_input = list(range(W))

if __name__ == '__main__':
    
    
    while ((UB-LB)>epsilon):
        
        x_sol = []
        for i in range(len(node_list)):
            if phaseI[i].x >= 1:
                x_sol.append(i)
                
        #print("---- iteration ------  " + str(iter))
        
    
        
        actual_spread=[]
        
        for i in escenarios_input:
            actual_spread.append(check_optimality(i,x_sol))
       
       
        incumbent=sum(actual_spread)/W  ##be aware of this W
        
        if (LB<incumbent):
            LB=incumbent
        
        
        m.write('model2.lp')
        phaseI= re_optimize()
        iter+=1
        UB=0
        for i in range(len(node), len(node)+ len(theta_w)):
                UB+=(phaseI[i].x)/(W) #####Be aware of this W
                
        print("UB***********************"+str(UB))
        if iter>=10000:
            break
    	


#
#
    phaseI = m.getVars()
    m.printAttr('X')
    set_seed = []
    for i in range(len(node_list)):
        if phaseI[i].x >= 1:
    
            set_seed.append(i+1)



# elapsed_time_fl = (time.time() - start)
# print("Total elapsed_time:  " + str(elapsed_time_fl))
# print(elapsed_time_fl)

# print("============================SEED==================")


# print(set_seed)

    UB=0
    for i in range(len(node), len(node)+ len(theta_w)):
        UB+=(phaseI[i].x)/(W)


    final_df=pd.Series(x_sol)
    
    
    final_df.to_pickle("final_data.pickle")
    
    with open('opt_spread.txt', 'w') as f:
        f.write("rate    " + str(UB))
    










