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
plate_num = 1
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

#Define number of blanks
num_blanks=int(df.iloc[0,3])

#Make Titration Concentration Dictionary
tit_conc=[]
for i in range(num_blanks):
    tit_conc.append(0)
tit_conc.extend(conc)

#Now, we have to calculates how many wells are used in a row.
num_used_wells=len(tit_conc)

#Now, we have to calculate how many wells remain in incomplete rows.
num_skip_wells = 24-num_used_wells

#Now, let's repeat our compound name as many times as there are titration concentrations. 
compound_list=[]
n=0
for i in range(len(comp)):
    for i in tit_conc:
        compound_list.append(df['Compound'][n])
    n+=1 

#Now, let's repeat a compound's MW as many times as it appears
p=0
mw_list = []
for i in range(len(comp)):
    for i in tit_conc:
        mw_list.append(mw[p])
    p+=1
    
#Now, let's get the complete concentration list
conc_list = []
for i in comp:
    conc_list.append(tit_conc)
conc_list=list(itertools.chain.from_iterable(conc_list))

#Now, let's make our used position list. 
r=0
position_list=[]
platenum_list=[]
for i in compound_list:
    position_list.append(pos[r])
    platenum_list.append(plate_num)
    if (r-num_used_wells+1)%24==0:
        r+=num_skip_wells
    if r==383:
        r=0
        plate_num+=1
    else:
        r+=1

#Now, let's make our final list    

if num_used_wells>24:
    error_message = 'You are overfilling the plate! Reduce number of concentrations, blanks or compounds.'
    df_error = {'Error':error_message}
    out_df = pd.DataFrame.from_dict(df_error,orient="index") 
    out_df = out_df.transpose()
    out_df.columns = ['Error']
    out_df.to_csv(output_file,header=out_df.columns,index=False)
    
else:
    df1 = {'Plate Number':platenum_list,'Compound':compound_list,'MW':mw_list,'Concentration':conc_list,'Position': position_list}
    out_df = pd.DataFrame.from_dict(df1,orient="index") 
    out_df = out_df.transpose()
    out_df.columns = ['Plate Number','Compound','MW','Concentration','Position']
    print('DataFrame:\n', out_df)
    out_df.to_csv(output_file,header=out_df.columns,index=False)

print(len(comp))
