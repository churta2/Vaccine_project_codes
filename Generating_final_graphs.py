#import pickle5 as pickle
import pickle
import os
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import pandas as pd
import random
from multiprocessing import Pool
import copy

# #========================================================

str1="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_project/cascades_WA/data_0.2_0.2_future/graph_"
str2=".pkl"




data=pd.read_csv('contingency.csv')
data=data[data['x']!=0]   ### Just consider combinations with positive values
data=data.reset_index()  
data=data[['category', 'x']]   ###Just these two columns
data=data.reset_index() 



#data=pd.read_csv('data_complete.csv')



O=[]

all_nodes=[]


#### This block generates random label to individuals inside each category


def cat_individuals(x):
    size = data['x'][x]

    s = list(range(int(size)))
    t= list(range(int(size)))
    O.append(t)
    
    random.shuffle(s)

    new_list = [(x, i) for i in s]
    new_list2 = [(x, u) for u in t]
    
    all_nodes.append(new_list2)

    return set(new_list)


indices = list(data.index)

sets_subsets = [cat_individuals(i) for i in indices]
data['subsets']=sets_subsets

#--------------------------------------------

#-------------Saving lists----------------


with open('set_O.pkl', 'wb') as f:
    pickle.dump(O, f,protocol=pickle.HIGHEST_PROTOCOL)


with open('set_I.pkl', 'wb') as f:
    pickle.dump(indices, f,protocol=pickle.HIGHEST_PROTOCOL)

al_nodes=sum(all_nodes, [])

with open('set_nodes.pkl', 'wb') as f:
    pickle.dump(al_nodes, f,protocol=pickle.HIGHEST_PROTOCOL)




data.to_csv('data_complete.csv')



#all_nodes=set()

# for i in indices:
#     all_nodes=all_nodes.union(data.loc[i,'subsets'])


sets_subsets2=list(data['subsets'])

sets_subsets=[eval(sets_subsets2[i]) for i in range(2882)]

####...........................UNTIL HERE..........................................##############
# sets_subsets=list(df_n['sub_sets'])

#### This function will re label all nodes from a graph and it will create a new file with
# the updated graph 
##########################



def built_graphs(k):
    print("analyzing graph"+str(k))
    str_t = str1 + str(k) + str2
    file = open(str_t, 'rb')
    G = pickle.load(file)

    copy_sets_subsets = copy.deepcopy(sets_subsets)

    nodes = list(G.nodes())

    for i in nodes:
        if (len(G.nodes[i]) == 0):
            G.remove_node(i)

    nodes = list(G.nodes())

   

    ## Relabels fips

    for i in nodes:
        new_fip = G.nodes[i]['fips'][0:5]
        G.nodes[i]['fips'] = new_fip
        # IS.add(G.nodes[i]['age'])

    nodes = list(G.nodes())

    keys = []
    values = []
    for i in nodes:
        keys.append(i)

        ele1 = G.nodes[i]['age']
        if (G.nodes[i]['occupation']=='nojob'):
            ele2 = 'unnecessary_workers'
        else:
            ele2 = G.nodes[i]['occupation']
            
        ele3 = G.nodes[i]['fips']

        tupla = (ele1, ele2, ele3)
        busq = str(tupla)

        which_group = list(data[data['category'] == busq].index)[0]
        assignation = set()
        assignation.add(list(copy_sets_subsets[which_group])[0])

        values.append(list(assignation)[0])

        new_subsets = copy_sets_subsets[which_group].difference(assignation)
        copy_sets_subsets[which_group] = new_subsets

    relabel_dict = {k: v for k, v in zip(keys, values)}
    G = nx.relabel_nodes(G, relabel_dict)

    # all_sets = list(copy_sets_subsets[0])

    # for t in range(1, len(copy_sets_subsets)):
    #     all_sets = all_sets + list(copy_sets_subsets[t])

    # G.add_nodes_from(all_sets)

    #name_updated = "/ihome/arahimian/cah259/Vaccine_project/graphs/graph_" + str(k) + ".pickle"
    
    name_updated = str1 + str(k) + ".pkl"

    with open(name_updated, 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)

for i in range(33):
    built_graphs(i)



####

# if __name__ == '__main__':
#     numbers = list(range(33))
#     pool = Pool(processes=1)
#     pool.map(built_graphs, numbers)
#     pool.close()



