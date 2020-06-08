import json
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
import pdb

#with open('expt_results/response_200519_1d.json') as f:
#  data = json.load(f)

data = pd.read_csv('./Results/MMDA Starmall April 23/\
starmall-20200423-counts/EDSA-STARMALL_20200423_0900-1100-17-counts.csv',sep=',');
#data.head()

fig, ax = plt.subplots()
data.plot(x='frameNum',y='blobCount', ax=ax)
#plt.xticks(np.arange(7,17,step=1/2)); 

#print(data)
#data = pd.DataFrame(data['activities-heart-intraday']['dataset']);


#data.plot(x='time',y='value',label='Heart Rate - May 19, 2020', ax=ax)
plt.show()

data = pd.read_csv('./Results/MMDA Starmall April 23/\
starmall-20200423-summaries/_all_v1.csv',sep=',');
#pdb.set_trace();
data.plot(x='Time',y='Vehicle_Counts', linewidth=2.0, c='r')
#plt.xticks(np.arange(700,1700,step=30))

# Show the major grid lines with dark grey lines
plt.grid(b=True, which='major', color='#666666', linestyle='-')

# Show the minor grid lines with very faint and almost transparent grey lines
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

plt.title('EDSA Starmall - April 23, 2020')
plt.show()


