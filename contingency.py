# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 10:07:00 2021

@author: usuario
"""

from gurobipy import *
import pandas as pd


######################

data=pd.read_csv('exploratory_future.csv')
data=data[['category','max_value']]


data['category']=data['category'].apply(eval)

to_del=[]
for i in range(data.shape[0]):
    
    tup=data.loc[i,'category']
    if (tup[1]=='nojob'):
        ele1=tup[0]
        ele2='unnecessary_workers'
        ele3=tup[2]
        tup2=(ele1,ele2,ele3)
        a=data[tup2==data['category']].index[0]
        to_del.append(i)

        data.loc[a,'max_value']=data.loc[a,'max_value']+data.loc[i,'max_value']

    

data=data.drop(data.index[to_del])

data=data.reset_index()
######################



#value_x=dict(data.values)



I=['60_61',
'62_64',
'65_66',
'67_69',
'70_74',
'75_79',
'80_84',
'85+',
'0_4',
'5_9',
'10_14',
'15_17',
'18_19',
'20',
'21',
'22_24',
'25_29',
'30_34',
'35_39',
'40_44',
'45_49',
'50_54',
'55_59']

J =['Management_business_and_financial_occupations',
'Computer_engineering_and_science_occupations',
'Education_legal_community_service_arts_and_media_occupations',
'Healthcare_practitioners_and_technical_occupations',
'Protective_service_occupations',
'Food_preparation_and_serving_related_occupations',
'Building_and_grounds_cleaning_and_maintenance_occupations',
'Personal_care_and_service_occupations',
'Sales_and_office_occupations',
'Natural_resources_construction_and_maintenance_occupations',
'Production_transportation_and_material_moving_occupations',
'unnecessary_workers']

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



age=[193606,
273282,
165885,
221912,
280470,
179870,
122786,
131970,
465390,
475222,
459521,
277374,
179124,
9960,
97356,
301465,
565733,
550151,
513391,
469105,
480554,
489510,
500470]

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
3809828]

fip=[25559,
29349,
255123,
99539,
97871,
611481,
5257,
138110,
54358,
9954,
11912,
2922,
12464,
94559,
107264,
40543,
2842363,
344873,
58897,
28113,
101103,
13711,
82287,
54709,
27962,
17369,
112977,
21644,
162805,
1527,
103356,
654172,
58094,
360915,
5504,
79146,
284875,
63848,
327592
]



sub_I=['67_69',
'70_74',
'75_79',
'80_84',
'85+',
'0_4',
'5_9',
'10_14',
'15_17']

sub_I2=['18_19',
'20',
'21',
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


sub_J=['Management_business_and_financial_occupations',
'Computer_engineering_and_science_occupations',
'Education_legal_community_service_arts_and_media_occupations',
'Healthcare_practitioners_and_technical_occupations',
'Protective_service_occupations',
'Food_preparation_and_serving_related_occupations',
'Building_and_grounds_cleaning_and_maintenance_occupations',
'Personal_care_and_service_occupations',
'Sales_and_office_occupations',
'Natural_resources_construction_and_maintenance_occupations',
'Production_transportation_and_material_moving_occupations']

sub_J2=['unnecessary_workers']


total=sum(age)

X=[(i,j,k) for i in I for j in J for k in K]



m = Model("table")

x=m.addVars(X, vtype=GRB.INTEGER, name="x_ijk")

z=m.addVar(vtype=GRB.INTEGER, name="z")


for i in I:
    t=I.index(i)
    m.addConstr(sum(x[i,j,k] for j in J for k in K) >= age[t])
    print(age[t])

for j in J:
    t=J.index(j)
    m.addConstr(sum(x[i,j,k] for i in I for k in K) == occ[t])
    

for k in K:
    t=K.index(k)
    m.addConstr(sum(x[i,j,k] for i in I for j in J) == fip[t])


for i in sub_I:
    for j in sub_J:
        m.addConstr(sum(x[i,j,k] for k in K) == 0)




for i in I:
    for j in J:
        for k in K:
            tupla=(i,j,k)
            min_val=int(data[data['category']==tupla]['max_value'])
            m.addConstr(x[i,j,k] >= min_val)



for i in I:
    for j in J:
        for k in K:
            m.addConstr(x[i,j,k] <=z)

            
m.write('cont.lp')

m.setObjective(z, GRB.MINIMIZE)

m.optimize()

# if m.SolCount> 0:
#     m.printAttr('X')


r = m.getVars()

df=pd.DataFrame()


for i in range(10764):
    
    splitted=(r[i].varName).split(',')
    
    temp={'category':(splitted[0][6:], splitted[1], splitted[2][0:5]), 'x': int(r[i].x)}
    df=df.append(temp,ignore_index=True)



df.to_csv('contingecy.csv')
