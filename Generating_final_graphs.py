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

# path="/ihome/arahimian/cah259/Vaccine_project"
# os.chdir(path)

# cat_age = ['60_61', '40_44', '62_64', '05_09', '15_17', '67_69', '75_79', '85+__', '55_59', '45_49',
#            '35_39', '70_74', '25_29', '30_34', '50_54', '65_66', '80_84', '20_00', '10_14', '18_19', '00_04',
#            '21_00', '22_24']
# cat_occ = ['education', 'product_trans_material_moving', 'healthcare', 'protective_service',
#            'computer', 'food_preparation', 'management', 'personsal_care', 'nojob', 'natural', 'unnecessary_workers',
#            'sales', 'building']

# cat_fips = ['53001', '53003', '53005', '53007', '53009', '53011', '53013', '53015', '53017', '53019',
#             '53021', '53023', '53025', '53027', '53029', '53031', '53033', '53035', '53037', '53039', '53041',
#             '53043', '53045', '53047', '53049', '53051', '53053', '53055', '53057', '53059', '53061', '53063',
#             '53065', '53067', '53069', '53071', '53073', '53075', '53077']

# t = [cat_age, cat_occ, cat_fips]
# ent = list(itertools.product(*t))

# data = [str(i) for i in ent]

# df = pd.DataFrame({'category': data})


str1="C:/Users/usuario/OneDrive - University of Pittsburgh/Fall_2021/Vaccine_Project/sf_new_march_data_WA/data_0.2_0.2/infectionRate_0.2_0.2_"

# #str1 = "/ihome/arahimian/cah259/Vaccine_project/cascades/infectionRate_0.2_0.2_"
str2 = ".pkl"

# # path="C:/Users/usuario/OneDrive - University of Pittsburgh/Networks/Vaccine_project"

# census = pd.read_csv('contingecy.csv')
# census = census.rename(columns={"cat": "category"})

# df2 = pd.read_csv('exploratory.csv')

# df = pd.merge(df2, census, how='left', on='category')

####...........................IF SAVED NOT REQUIRED....................................#


# for k in range(100,176):


#     col_name="data_"+str(k)
#     df[col_name]=df['x']-df[col_name]

# df_n=df[df['x']!=0]

# df_n=df_n.reset_index()



# #========================================================

#df_n.to_pickle("C:/Users/usuario/OneDrive - University of Pittsburgh/Networks/Vaccine_project/condensed.pkl")

df_n = pd.read_pickle("C:/Users/usuario/OneDrive - University of Pittsburgh/Networks/Vaccine_project/condensed.pkl")

O=[]

for i in range(int(3500)):
    temporal_list=list(range(int(df_n['x'][i])))
    O.append(temporal_list)

# def cat_individuals(x):
#     size = df_n['x'][x]

#     s = list(range(int(size)))
#     random.shuffle(s)

#     new_list = [(x, i) for i in s]

#     return set(new_list)


# indices = list(df_n.index)

# sets_subsets = [cat_individuals(i) for i in indices]


sets_subsets= list(df_n['sub_sets'])



####...........................UNTIL HERE..........................................##############
# sets_subsets=list(df_n['sub_sets'])

def built_graphs(k):
    str_t = str1 + str(k) + str2
    file = open(str_t, 'rb')
    G = pickle.load(file)

    copy_sets_subsets = copy.deepcopy(sets_subsets)

    nodes = list(G.nodes())

    for i in nodes:
        if (len(G.nodes[i]) == 0):
            G.remove_node(i)

    nodes = list(G.nodes())

    ##fix data format for age

    for i in nodes:
        if ((G.nodes[i]['age'] == '85+')):
            # print(i)
            G.nodes[i]['age'] = '85+__'
        elif ((G.nodes[i]['age'] == '0_4')):
            # print(i)
            G.nodes[i]['age'] = '00_04'
        elif ((G.nodes[i]['age'] == '5_9')):
            # print(i)
            G.nodes[i]['age'] = '05_09'
        elif ((G.nodes[i]['age'] == '20')):
            # print(i)
            G.nodes[i]['age'] = '20_00'
        elif ((G.nodes[i]['age'] == '21')):
            # print(i)
            G.nodes[i]['age'] = '21_00'
        else:
            pass

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
        ele2 = G.nodes[i]['occupation']
        ele3 = G.nodes[i]['fips']

        tupla = (ele1, ele2, ele3)
        busq = str(tupla)

        which_group = list(df_n[df_n['category'] == busq].index)[0]
        assignation = set()
        assignation.add(list(copy_sets_subsets[which_group])[0])

        values.append(list(assignation)[0])

        new_subsets = copy_sets_subsets[which_group].difference(assignation)
        copy_sets_subsets[which_group] = new_subsets

    relabel_dict = {k: v for k, v in zip(keys, values)}
    G = nx.relabel_nodes(G, relabel_dict)

    all_sets = list(copy_sets_subsets[0])

    for t in range(1, len(copy_sets_subsets)):
        all_sets = all_sets + list(copy_sets_subsets[t])

    G.add_nodes_from(all_sets)

    #name_updated = "/ihome/arahimian/cah259/Vaccine_project/graphs/graph_" + str(k) + ".pickle"
    
    name_updated = "C:/Users/usuario/OneDrive - University of Pittsburgh/Networks/Vaccine_project/graphs/graph_" + str(k) + ".pkl"

    with open(name_updated, 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)





####

if __name__ == '__main__':
    numbers = list(range(100, 101))
    pool = Pool(processes=1)
    pool.map(built_graphs, numbers)
    pool.close()



