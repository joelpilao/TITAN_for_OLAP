#!/usr/bin/env python

## generates the whole-day totals from the 5-min -counts.csv files in specific sites specified by individual folders
## (c) Joel P. Ilao  7 June 2020
## usage: generateDayTotals.py -i <inputFilesList> -o <outputFolder>
## notes:
## 1) it will use default parameters if input parameters are not specified
## 2) highly suggested to use the generateInputFiles.sh script to generate the inputFilesList.
## 3) default input data folder used is ../_DATA/ while the output folder is ./_Output/
##
## ver 1.0.1 added new Hour chunks to the list, refined the time stamping of data chunks to accommodate those starting or ending with hour-fractions (e.g. 0900-1236, 1236-1408, etc.)

import json
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
import re
import pdb
import pandas as pd
import os.path 
from os import path
import sys, getopt

#default input parameters and settings global variables
outputFolder = './_Output/'
outName = '_all_';
outNameSubTotals = '_subTotals_';
sFileExt = '-counts.csv'; #file extension 

#create a chronologically ordered list of filenames first
sMainStem = 'EDSA-STARMALL_20200423_';
lTimeDuration = ['0700-0900', '0700-1408','0700-1436','0900-1000',\
	'1000-1100','0900-1100','1000-1200','1100-1300','1200-1400','1300-1500',\
	'1400-1600','1408-1700','1500-1700','1600-1800','0700-1200','1200-1700',\
	'1436-1700','1700-1800'];
lChunkIdx = np.arange(0,61);8


def convToRealTime(dataset,startTime,Ts):
	#convert the number of seconds elapsed to actual time
	actualTime = [];
	nSeconds = 0;
	nMinutes = 0;
	nHours = 0;
	
	bFlag = False;
	
	#split the start time to hour and minutes first and initialize variables correspondingly
	nMinutes =  ((startTime - np.floor(startTime))*60).astype('int32'); 
	startTime = np.floor(startTime).astype('int32');
	
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

def processDataFolder(fFullPathName,sMainStem):
	fOut = open(outName, 'a+');
	dataset = pd.DataFrame();
	dsSubTotals = pd.DataFrame(); #sub-totals every ~5 mins
	
	for i in lTimeDuration: #major chunks of hour intervals
		datasetChunk = pd.DataFrame();
		dsChunkSubTotals = pd.DataFrame();
		for j in lChunkIdx: # ~5-min intervals
			fCurrName = str(i) + '-' + str(j) + sFileExt;
			if not path.exists(fFullPathName + fCurrName):
				print('cannot find file '+fFullPathName + fCurrName + '. Skipping...');
				break; #meaning reached the max chunk
			print(fCurrName);
			currFileData = pd.read_csv(fFullPathName + fCurrName, sep=',');
			
			
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
		if (len(datasetChunk.index) == 0):
			continue; #move on to the next major time chunk, i.e. 0900-1100 etc.
		startHour = int(re.search('^([0-9]{2})',i).group(1));
		startHourMins = int(re.search('^[0-9]{2}([0-9]{2})',i).group(1)); #add fraction-of-an-hour information, e.g. 36 mins from 1436H 
		
		endHour = int(re.search('-([0-9]{2}).*$',i).group(1));
		endHourMins = int(re.search('^[0-9]{2}([0-9]{2})',i).group(1));
		
		startHour = startHour + float(startHourMins)/60;
		endHour = endHour + float(endHourMins)/60;
		
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
			
	print('saving output to ' + outputFolder + outName + sMainStem + '.csv')
	dataset.to_csv(outputFolder + outName + sMainStem + '.csv');
	dsSubTotals.to_csv(outputFolder + outNameSubTotals + sMainStem + '.csv');
	fOut.close();


def main():
	
	inputFList = [];

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["inputList=","outputFolder="])
	except getopt.GetoptError as err:
		print('generateDayTotals.py -i <inputList> -o <outputFolder>');
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('usage: generateDayTotals.py -i <inputList> -o <outputFolder>');
			sys.exit();	
		elif opt in ('-i', '--inputList'):
			#read contents of input file list
			fInList = arg;	
			print('input list file name is ' + arg);
			with open(fInList,'r') as fLine:
				tmp = fLine.readlines();
				for fName in tmp:
					#pdb.set_trace();
					if (re.search('^#',fName)): #if # is found at start of string (commented out), then skip
						print ('Not processing: ' + fName);
						continue;
					inputFList.append(fName.strip());
		elif opt in ('-o','outputFolder'): 	
			print('input folder is ' + arg);

        
	for fFullPathName in inputFList:
		print(fFullPathName);
		sMainStem = re.search('^(.*\/)(.*)-counts\/.*$',fFullPathName).group(2);
		print("sMainStem is " + sMainStem);
		processDataFolder(fFullPathName,sMainStem);
    		

if __name__ == "__main__":
    main()
