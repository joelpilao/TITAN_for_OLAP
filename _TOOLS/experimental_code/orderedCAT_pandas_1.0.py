import json
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
import re
import pdb
import pandas as pd
import os.path 
from os import path


def convToRealTime(dataset,startTime,Ts):
	#convert the number of seconds elapsed to actual time
	actualTime = [];
	nSeconds = 0;
	nMinutes = 0;
	nHours = 0;
	
	bFlag = False;
	for ind in dataset.index:
		actualTime.append(str(startTime + nHours) + ':' + str(nMinutes) + ':' + str(np.floor(nSeconds).astype('int32')));
		nSeconds += Ts;
		if ( (nSeconds - 60) >= 0):
			while ((nSeconds - 60) >= 0):
				nMinutes += 1;
				nSeconds -= 60;
			bFlag = True;
		if ( (nMinutes - 60) >= 0 and bFlag == True):
			while ( (nMinutes - 60) >= 0):
				nHours += 1;
				#pdb.set_trace();
				nMinutes = 0;
			bFlag = False;
		#pdb.set_trace();
		
	#pdb.set_trace();
	dataset['Time'] = actualTime;
			
	return dataset;

#output name
outName = '_all_v2';
outNameSubTotals = '_all_v2_subTotals';
sFileExt = '-counts.csv'; #file extension 

#create a chronologically ordered list of filenames first 
sMainStem = 'EDSA-STARMALL_20200423_';
lTimeDuration = ['0700-0900','0900-1100','1100-1300','1300-1500','1500-1700'];
#lTimeDuration = ['0700-1200','1200-1700'];
lChunkIdx = np.arange(0,24);

fOut = open(outName, 'a+');



dataset = pd.DataFrame();
dsSubTotals = pd.DataFrame(); #sub-totals every ~5 mins

for i in lTimeDuration: #major chunks of hour intervals
	datasetChunk = pd.DataFrame();
	dsChunkSubTotals = pd.DataFrame();
	for j in lChunkIdx: # ~5-min intervals
		fCurrName = str(i) + '-' + str(j) + sFileExt;
		if not path.exists(sMainStem + fCurrName):
			break;
		print(fCurrName);
		currFileData = pd.read_csv(sMainStem + fCurrName, sep=',');
	
	
		###determine common columns (note: only set if you want to plot common columns
		#common_cols = dataset.columns.intersection(currFileData.columns);
		##append data of common columns of current file to the running aggregate dataset
		#df_list = [dataset[common_cols],currFileData[common_cols]];
		
		df_list = [datasetChunk, currFileData];
		datasetChunk = pd.concat(df_list,ignore_index=True); #simply concatenate, not enforcing original indices
		#pdb.set_trace();
		
		#do the same for sub-totals 
		df_list = [dsChunkSubTotals, currFileData.tail(1)];
		dsChunkSubTotals = pd.concat(df_list,ignore_index=True);

	#place actual time slots
	#pdb.set_trace();
	startHour = int(re.search('^([0-9]{2})',i).group(1));
	endHour = int(re.search('-([0-9]{2}).*$',i).group(1));
	nPerHour = len(datasetChunk.index)/(endHour - startHour); # num samples per hour 
	Ts = 60*60/nPerHour # sampling period (in secs / sample)
	datasetChunk = convToRealTime(datasetChunk,startHour,Ts);
	
	df = [dataset, datasetChunk]
	dataset = pd.concat(df,ignore_index=True);
	#pdb.set_trace();
	
	#pdb.set_trace();
	nPerHour = len(dsChunkSubTotals.index)/(endHour - startHour);
	Ts = 3600/nPerHour;
	#pdb.set_trace();
	dsChunkSubTotals = convToRealTime(dsChunkSubTotals,startHour,Ts);
	
	df = [dsSubTotals, dsChunkSubTotals];
	dsSubTotals = pd.concat(df, ignore_index=True);
	
	
dataset.to_csv(outName + sMainStem + '.csv');
dsSubTotals.to_csv(outNameSubTotals + sMainStem + '.csv');
fOut.close();

