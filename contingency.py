# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 10:07:00 2021

@author: usuario
"""

from gurobipy import *
import pandas as pd


df=pd.read_csv('exploratory.csv')

sub_df=df[['category','max_value']]

value_x=dict(sub_df.values)



I=['60_61',
'62_64',
'65_66',
'67_69',
'70_74',
'75_79',
'80_84',
'85+__',
'00_04',
'05_09',
'10_14',
'15_17',
'18_19',
'20_00',
'21_00',
'22_24',
'25_29',
'30_34',
'35_39',
'40_44',
'45_49',
'50_54',
'55_59']

J =['management',
'computer',
'education',
'healthcare',
'protective_service',
'food_preparation',
'building',
'personsal_care',
'sales',
'natural',
'product_trans_material_moving',
'unnecessary_workers',
'nojob']

K=['53001',
'53003',
'53005',
'53007',
'53009',
'53011',
'53013',
'53015',
'53017',
'53019',
'53021',
'53023',
'53025',
'53027',
'53029',
'53031',
'53033',
'53035',
'53037',
'53039',
'53041',
'53043',
'53045',
'53047',
'53049',
'53051',
'53053',
'53055',
'53057',
'53059',
'53061',
'53063',
'53065',
'53067',
'53069',
'53071',
'53073',
'53075',
'53077']



age=[260153,
367215,
222903,
298188,
376874,
241695,
164990,
177331,
625355,
638566,
617468,
372713,
240693,
13383,
130820,
405085,
760188,
739250,
689855,
630347,
645730,
657765,
672493]

occ=[607327,
315985,
382159,
320430,
63918,
197449,
117859,
99885,
710533,
345835,
432899,
3809828,
2544953]

fip=[34344,
39437,
342814,
133753,
131511,
821660,
7064,
185581,
73043,
13376,
16007,
3927,
16748,
127062,
144133,
54478,
3819345,
463413,
79141,
37776,
135854,
18424,
110571,
73514,
37573,
23339,
151809,
29084,
218764,
2052,
138882,
879025,
78062,
484969,
7396,
106350,
382793,
85794,
440192]




sub_I=['67_69',
'70_74',
'75_79',
'80_84',
'85+__',
'00_04',
'05_09',
'10_14',
'15_17']

sub_I2=['18_19',
'20_00',
'21_00',
'22_24',
'25_29',
'30_34',
'35_39',
'40_44',
'45_49',
'50_54',
'55_59',
'60_61',
'62_64',
'65_66']


sub_J=['management',
'computer',
'education',
'healthcare',
'protective_service',
'food_preparation',
'building',
'personsal_care',
'sales',
'natural',
'product_trans_material_moving',
'unnecessary_workers']

sub_J2=['nojob']


total=sum(age)

X=[(i,j,k) for i in I for j in J for k in K]



m = Model("table")

x=m.addVars(X, vtype=GRB.INTEGER, name="x_ijk")

z=m.addVar(vtype=GRB.INTEGER, name="z")


# for i in I:
#     t=I.index(i)
#     m.addConstr(sum(x[i,j,k] for j in J for k in K) >= age[t])
#     print(age[t])

for j in J:
    t=J.index(j)
    m.addConstr(sum(x[i,j,k] for i in I for k in K) == occ[t])
    

for k in K:
    t=K.index(k)
    m.addConstr(sum(x[i,j,k] for i in I for j in J) == fip[t])


for i in sub_I:
    for j in sub_J:
        m.addConstr(sum(x[i,j,k] for k in K) == 0)


for i in sub_I2:
    for j in sub_J2:
        m.addConstr(sum(x[i,j,k] for k in K) == 0)


for i in I:
    for j in J:
        for k in K:
            get_key="('"+str(i)+"', '"+str(j)+"', '"+str(k)+"')"
            m.addConstr(x[i,j,k] >= value_x[get_key])



for i in I:
    for j in J:
        for k in K:
            m.addConstr(x[i,j,k] <=z)

            
m.write('cont.lp')

m.setObjective(sum(x[i,j,k] for i in I for j in J for k in K)+ z, GRB.MINIMIZE)

m.optimize()

# if m.SolCount> 0:
#     m.printAttr('X')


r = m.getVars()

df=pd.DataFrame()


for i in range(11661):
    temp={'cat':(r[i].varName[6:11], r[i].varName[12:-7],r[i].varName[-6:-1]), 'x': r[i].x}
    df=df.append(temp,ignore_index=True)



df.to_csv('contingecy.csv')
