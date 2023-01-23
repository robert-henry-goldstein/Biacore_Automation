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

#print(pos)

# Now, let's set some placeholders.
plate_num = 0
well_num=0
platenum_list=[]

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
comp=df['Compound'].tolist()
conc=df['Concentration'].dropna().tolist()
mw=df['MW'].tolist()

#Define number of blank sets. We'll print the blank rows as many times as there blanks sets.
num_blanks=int(df.iloc[0,3])

#Calculate number of repeats
numRepeats=num_blanks+1

#Make blank rows
blank_row=[0]*len(conc)

#Make the row of dose concentrations:
doses = num_blanks*blank_row + conc

#Count the number of lines:
numLines = numRepeats*len(comp)

#Now, we have to calculate how many wells remain in incomplete rows.
num_skip_wells = 24-len(doses)

#Calculate plate row length:
row_length = len(doses)

#Now, let's repeat our compound name as many times as there are titration concentrations. 
#We also increment our well number and plate number.
compound_list = []

for i in comp:
    compound_list=compound_list+numRepeats*[i]
       
#print(compound_list)

#Now, let's make our plate number list.

for i in comp:
    for j in range(numRepeats):
        platenum_list.append(plate_num+1)
        well_num+=len(conc)
        if (well_num+num_skip_wells)%24==0:
            well_num+=num_skip_wells
        if well_num%384==0 and well_num!=0:
            plate_num+=1 
                     
#print(platenum_list)

#Now, let's make the dataframe of MW.
p=0
mw_list = []
for i in comp:
    for i in range(numRepeats): #THIS RANGE COULD BE WRONG
        mw_list.append(mw[p])
    p+=1 
  
#print(mw_list)    
  
#Now, let's get the list of list of positions. It loops back to A1 once it hits 384 wells.
r=0
position_list=[]
for i in range(numLines):
    position_list.append([])
    for j in conc: 
        position_list[i].append(pos[r])
        if (r-len(doses)+1)%24==0:
            r+=num_skip_wells
        if r==383:
            r=0
        else:
            r+=1
#print(position_list)

#Now, let's make our concentration df.
w=1
df_conc_columns=[]
for i in conc:
    clmn_name="Concentration_{}".format(w)
    df_conc_columns.append(clmn_name)
    w+=1
df_conc=pd.DataFrame(columns=df_conc_columns)

for i in comp:
    for i in range(num_blanks):
        df_conc.loc[len(df_conc.index)] = blank_row
    df_conc.loc[len(df_conc.index+1)]=conc
    
#print(df_conc)

#Now, let's make our position df.
x=1
df_pos_columns=[]
for i in conc:
    clmn_name="Position_{}".format(x)
    df_pos_columns.append(clmn_name)
    x+=1
df_pos=pd.DataFrame(columns=df_pos_columns)

c=0
for i in comp:
    for i in range(numRepeats): 
        df_pos.loc[len(df_pos.index)] = position_list[c]
        c+=1
        if c==16*numRepeats:
            c=0

#print(df_pos)

#Let's prevent the number of wells in a row from exceding 24:

if row_length>24:
    error_message = 'You are overfilling the rows! Reduce the number of concentrations or blanks.'
    df_error = {'Error':error_message}
    out_df = pd.DataFrame.from_dict(df_error,orient="index") 
    out_df = out_df.transpose()
    out_df.columns = ['Error']
    out_df.to_csv(output_file,header=out_df.columns,index=False)

#Now, let's combine our dataframes.
else:
    df = {'Plate Number':platenum_list,'Compound':compound_list,'MW':mw_list}
    out_df = pd.DataFrame.from_dict(df,orient="index") 
    out_df = out_df.transpose()
    out_df.columns = ['Plate Number','Compound','MW']
    out_df=pd.concat([out_df,df_pos,df_conc],axis=1,verify_integrity=True,ignore_index=False)
    print('DataFrame:\n',out_df)
    out_df.to_csv(output_file,header=out_df.columns,index=False)


