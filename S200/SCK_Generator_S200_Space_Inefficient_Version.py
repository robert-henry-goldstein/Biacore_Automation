import pandas as pd
import os
import itertools
from math import trunc

#Make the plate map positions
position = list(itertools.product(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'], range(1,25)))
pos=[]

for i,j in position:
    res = i+str(j)
    pos.append(res)

# Now, let's set some placeholders.
well_num=0
platenum_list=[]
comp = []
mw = []
conc = []

def increment_file_name(file_name):
    name, ext = os.path.splitext(file_name)
    try:
        # increment the file name if it already exists
        name, num = name.rsplit('_', 1)
        num = str(int(num) + 1).zfill(2)
    except ValueError:
        num = "01"
    return name + "_" + num + ext

#Define the input and output files
input_file = "input.csv"
#Now, let's generate our output file name format.
output_file = "output_01.csv"

while os.path.exists(output_file):
    output_file = increment_file_name(output_file)

#Now, let's read our input file.
df = pd.read_csv (input_file)
df.columns = ['Compound','Concentration', 'MW','Blanks']


#Now, let's fill in our initial compound,concentration, and MW lists.
comp.extend(df['Compound'].tolist())
conc.extend(df['Concentration'].dropna().tolist())
mw.extend(df['MW'].tolist())

#Get length of compound list
z=len(comp)

#Define number of blank sets
num_blanks=int(df.iloc[0,3])

#Make Titration Concentration Dictionary
doses=[]
for i in conc:
    doses.append(0)
doses=doses*num_blanks
doses.extend(conc)

# Now, we have to calculates how many wells are used in a row.
num_used_wells = len(doses)

# Now, we have to calculate how many wells remain in incomplete rows.
num_skip_wells = 24-num_used_wells

#Now, we need to calculate the plate capacity:
plate_capacity=16

#Now, let's repeat our compound name as many times as there are titration concentrations. 
#We also increment our well number and plate number.
compound_list=[]
n=0
for i in range(z):
    for i in doses:
        compound_list.append(df['Compound'][n])
    n+=1 

#Now, let's repeat a compound's MW as many times as it appears
p=0
mw_list = []
for i in range(z):
    for i in doses:
        mw_list.append(mw[p])
    p+=1
    
#Now, let's get the complete concentration list
conc_list = []
for i in comp:
    conc_list.append(doses)
conc_list=list(itertools.chain.from_iterable(conc_list))

#Now, let's make our used position list. It stops once the plate is full. 
r=0
position_list=[]
for i in compound_list:
    position_list.append(pos[r])
    if (r-num_used_wells+1)%24==0:
        r+=num_skip_wells
    if r==383:
        break
    else:
        r+=1

#Now, let's make our final list 
if num_used_wells > 24 or len(comp)>plate_capacity:
    error_message = 'You are overfilling the rows! Reduce the number of concentrations or blanks.'
    df_error = {'Error': error_message}
    out_df = pd.DataFrame.from_dict(df_error, orient="index")
    out_df = out_df.transpose()
    out_df.columns = ['Error']
    out_df.to_csv(output_file, header=out_df.columns, index=False)   

else:
    df1 = {'Compound':compound_list,'MW':mw_list,'Concentration':conc_list,'Position': position_list}
    out_df = pd.DataFrame.from_dict(df1,orient="index") 
    out_df = out_df.transpose()
    out_df.columns = ['Compound','MW','Concentration','Position']
    print('DataFrame:\n', out_df)
    out_df.to_csv(output_file,header=out_df.columns,index=False)


