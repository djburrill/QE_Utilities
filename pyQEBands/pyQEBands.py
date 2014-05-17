''' 
pyQEBands_v1.01

Author: Daniel Burrill
Date Created: May 5, 2014
Date Last Modified: May 17, 2014

v1.01
- Added some new features to streamline execution

v1.00
- Initial Build. Combined many of the previous band structure analysis
  tools built for QE
  
Description:
 Uses 'bands' output data to create a csv file containing band structure
 data. The 'bands' file must have verbosity set to high in order to
 generate the eigenenergies at the k points. Also, the path to the 
 Projwfc.x program in the properties folder of QE must be known in order
 to calculation projected wavefunctions.
 
 Successful execution depends highly on the format of the output file.
 If this has been changed due to being a different version, this will
 output nonsense values or fail.

'''

## Imports
import pyLines
import subprocess
import copy
import os
import argparse
import pyInput

## Functions
def fGetInput():
	## Variables
	
	## Engine
	# Initiate Parser
	parser = argparse.ArgumentParser()
	parser.add_argument("keyInput", help="String containing the name of the input file with extension")
	args = parser.parse_args()
	
	return args.keyInput
	
def fGatherEigenData(inFileName,query):
	'''
	RETURN
	dbands: Dictionary containing k point and eigen energy information
	dbands :: {'kpoint_num':[eigen energy list],...}
	'''
	
	## Variables
	lBandInfo = []
	lBands = []
	lBandsEnergy = []
	dBands = {}
	iKPoint = 1
	swKpoint = False

	## Read In Output File
	# Use pyLines to Exctract Useful Info
	lBandInfo = pyLines.pyBlocks(query,inFileName)

	## Format Band Information
	# Remove white space and end lines
	for index,entry in enumerate(lBandInfo[0]):
		lBandInfo[0][index] = entry.strip().split()

	# Remove Header and empty elements
	# Run twice to be sure
	for runs in range(2):
		for index,entry in enumerate(lBandInfo[0]):
			if (lBandInfo[0][index] == ['End', 'of', 'band', 'structure', 'calculation']) or (lBandInfo[0][index] == []):
				del lBandInfo[0][index]

	## Gather Useful Information
	for index,entry in enumerate(lBandInfo[0]):
		# If K Point
		if ('k' in entry) and (swKpoint == True):
			lBands.append(lBandsEnergy)
			dBands[str(iKPoint)] = lBands
			iKPoint += 1

			# Check for Negative Values
			if (len(entry[1]) <= 1):
				lBands = [[entry[2],entry[3],entry[4]]]
			else:
				lBands = [[entry[1][1:],entry[2],entry[3]]]

			lBandsEnergy = []
	
		# If First K Point
		elif ('k' in entry) and (swKpoint == False):
			# Check for Negative Values
			if (len(entry[1]) <= 1):
				lBands = [[entry[2],entry[3],entry[4]]]
			else:
				lBands = [[entry[1][1:],entry[2],entry[3]]]

			swKpoint = True
			
		elif (index == len(lBandInfo[0])-1):
			for energy in entry:
				lBandsEnergy.append(energy)
				lBands.append(lBandsEnergy)
				dBands[str(iKPoint)] = lBands
			break				
	# If Energy
		else:
			for energy in entry:
				lBandsEnergy.append(energy)

	return dBands

def fProjwfc(projPath,pwfcOutputFile,pwfcOutputStd,pwfcInput):
	## Variables
	callStr = projPath + ' <' + pwfcInput +'> ' + pwfcOutputStd

	## Create Input File
	inFilePwfc = open(pwfcInput,'w')

	inFilePwfc.write('&PROJWFC\n')
	inFilePwfc.write(" filproj = '" + pwfcOutputFile + "' ,\n")
	inFilePwfc.write(' lwrite_overlaps = .true. ,\n')
	inFilePwfc.write('/\n')

	inFilePwfc.close()

	## Run Projwfc.x
	subprocess.check_call(callStr,shell=True)

def fGatherWfcData(inFileName):
	'''
	RETURN
	wfcDict: Dictionary containing kpoints, and eigen energies for each state
	wfcDict :: {state_int:{kpt_int:[eigen energies],...},...}
	'''
	
	## Variables
	dataArray = []
	header = []
	wfcDict = {}

	# Open File
	inFile = open(inFileName,'r')

	# Grab Lines From File
	for index,line in enumerate(inFile):
		# Format Line
		line = line.strip().split()

		# Ignore empty lines
		if (line == []):
			continue
		else:
			dataArray.append(line)

	# Close File
	inFile.close()

	# Separate Out Header
	for index,line in enumerate(dataArray):
		# Stop when line has length of two
		if (len(line) != 2):
			header.append(line)
		else:
			header.append(line)
			break

	# Trim dataArray
	for index,line in enumerate(header):
		if (line in dataArray):
			dataArray.remove(line)
	
	## Translate dataArray into dictionary
	kList = []
	kDict = {}
	OccList = []
	kpt = 0
	state = 0
	
	for index,line in enumerate(dataArray):
		# Change State
		if (len(line) != 3):
			if (index != 0):
				kDict[kpt] = OccList
				wfcDict[state] = kDict
				state += 1
				
			kpt = 0
			kDict = {}
			OccList = []
		
		# Check if kpt Changed
		if (len(line) == 3):
			if (kpt+1 != int(line[0])):
				kDict[kpt] = OccList
				OccList = []
				kpt = int(line[0])-1
				OccList.append(line[2])
			else:
				OccList.append(line[2])
				
		# If Last Value
		if (index == len(dataArray)-1):
			kDict[kpt] = OccList
			wfcDict[state] = kDict
			
	return wfcDict

def deriv(vector):
	dVec = []

	for index,point in enumerate(vector):
		if (index != len(vector)-1):
			dV = (float(vector[index+1])-float(point))/(index+1-index)
			dVec.append(dV)

	return dVec

def findBreaks(vector):
	breakList = []
	thresh = .1

	# Find Jumps
	for index,element in enumerate(deriv(vector)):
		if (element > thresh):
			breakList.append(index)

	return breakList

def fwfcDict2bandArray(wfcDict):
	## Variables
	numBands = len(wfcDict[1][1])
	numKpts = len(wfcDict[1])
	numStates = len(wfcDict)
	bandArray = []
	stateArray = []
	kptArray = []
	
	## Engine
	# Iterate through bands
	for band in range(numBands):
		stateArray = []
		# Iterate through states
		for state in range(numStates):
			kptArray = []
			# Iterate through kpts
			for kpt in range(numKpts):
				kptArray.append(wfcDict[state][kpt][band])
				
			stateArray.append(kptArray)
			
		bandArray.append(stateArray)
		
	return bandArray
		
def fFindSwaps(wfcDict):
	'''
	RETURN
	swapList: List containing band swap information at k points. Sorted by kpoint
	swapList :: [[band_int1,band_int2,kpoint_int],...]
	'''
	
	## Variables
	plotData = []
	swapList = []
	bandArray = fwfcDict2bandArray(wfcDict)
	
	# bandArray :: [[[State1_int,Band1_int eigen energies],[State2_int,Band1_int eigen energies],...],...]

	# Identify Jumps
	jumpArray = []

	for index1,band in enumerate(bandArray):
		jumpStateArray = []

		for index2,state in enumerate(band):
			jumpStateArray.append(findBreaks(state))

		jumpArray.append(jumpStateArray)

	# Sort jumpArray
	bandJumpArray = []

	for index1,band in enumerate(jumpArray):
		dmyArray = []

		for index2,jumpList in enumerate(band):
			for index3,breaks in enumerate(jumpList):
				if (breaks not in dmyArray):
					dmyArray.append(breaks)

		# Remove Adjacent Entries
		removed = 0
		dmyArray = sorted(dmyArray)
		for index4,element in enumerate(dmyArray):
			# Check Forward
			if ((index4-removed) < len(dmyArray)-1):
				if (abs(dmyArray[index4-removed]-dmyArray[index4-removed+1]) == 1):
					dmyArray.pop(index4-removed+1)
					removed += 1

		bandJumpArray.append(dmyArray)

	# Create List of Swaps    
	for index1,band1 in enumerate(bandJumpArray):
		for index2,band2 in enumerate(bandJumpArray):
			for index3,jump1 in enumerate(band1):
				for index4,jump2 in enumerate(band2):
					# Do not search if same band
					if (index1 != index2):
						swap12 = [index1,index2,jump1]
						swap21 = [index2,index1,jump1]
						if (jump1 == jump2) and (swap12 not in swapList) and (swap21 not in swapList):
							swapList.append(swap12)

	# Sort SwapList by K Point order
	return sorted(swapList, key=lambda swap: swap[2])

def fFilterSwaps(swaps):
	## Variables
	prevBands = []
	swapsOrig = copy.deepcopy(swaps)

	## Engine
	for bandSwap in swapsOrig:
		# If band not encountered previously add bands to prevBands list
		if (bandSwap[0] not in prevBands) and (bandSwap[1] not in prevBands):
			prevBands.append(bandSwap[0])
			prevBands.append(bandSwap[1])
		# Remove swap if encountered bands
		else:
			swaps.remove(bandSwap)
			
	print swaps

	return swaps		

def fSwap(swaps,eigenstate,wfcData):
	## Variables
	numKPoints = len(eigenstate)
	numStates = len(wfcData)
	numKpts = len(wfcData[1])

	## Engine
	# Swap Eigenstate Bands
	for bandSwap in swaps:
		for kpoint in range(bandSwap[2]+1,numKPoints):
			eigenstate[str(kpoint+1)][1][bandSwap[0]], eigenstate[str(kpoint+1)][1][bandSwap[1]] = eigenstate[str(kpoint+1)][1][bandSwap[1]], eigenstate[str(kpoint+1)][1][bandSwap[0]]

	# Swap wfcData
	# Iterate over swaps
	for swapData in swaps:
		# Iterate over states
		for state in range(numStates):
			# Swap Bands with kpts >= swap kpoint
			for kptSwap in range(swapData[2]+1,numKpts):
				wfcData[state][kptSwap][swapData[0]],wfcData[state][kptSwap][swapData[1]] = wfcData[state][kptSwap][swapData[1]],wfcData[state][kptSwap][swapData[0]]			
	
	return eigenstate,wfcData

def fOutput(outFileName,eigenstate):
	## Variables
	numBands = len(eigenstate['1'][1])
	numKPoints = len(eigenstate)

	## Engine
	# Open Output File
	outFile = open(outFileName,'w')

	# Build Header
	headerStr = '# Kpoint,'

	for bandIndex in range(numBands):
		# If Last, Endline
		if (bandIndex == range(numBands)[-1]):
			headerStr += 'Band ' + str(bandIndex) + '\n'
		else:
			headerStr += 'Band ' + str(bandIndex) + ','

	# Write to Outfile
	outFile.write(headerStr)

	for kpoint in range(numKPoints):
		outStr = str(kpoint) + ','

		for index,eigenEnergy in enumerate(eigenstate[str(kpoint+1)][1]):
			# If Last, Endline
			if (index == len(eigenstate[str(kpoint+1)][1])-1):
				outStr += str(eigenEnergy) + '\n'
			else:
				outStr += str(eigenEnergy) + ','

		outFile.write(outStr)	

	# Close Output File
	outFile.close()

## Main
if (__name__ == '__main__'):
	## Variables
	# Gather Input Variable Arguments
	varInputFileName = fGetInput()
	
	# Eigen System Vars
	header = pyInput.fKeyword('header',varInputFileName)[0].split()
	footer = pyInput.fKeyword('footer',varInputFileName)[0].split()
	inFileName = pyInput.fKeyword('inFileName',varInputFileName)[0]
	query = [[header,footer]]
	
	# Projwfc Vars
	pwfcPath = pyInput.fKeyword('pwfcPath',varInputFileName)[0]
	pwfcOutputFile = pyInput.fKeyword('pwfcOutputFile',varInputFileName)[0]
	pwfcOutputStd = pyInput.fKeyword('pwfcOutputStd',varInputFileName)[0]
	pwfcInput = pyInput.fKeyword('pwfcInput',varInputFileName)[0]
	
	# Wavefunction Vars
	wfcData = []
	numBands = 0

	# Find Swaps Vars
	swaps = []
	
	# Swap Cycle Vars
	cycleNum = 1

	# Output Vars
	outFileName = pyInput.fKeyword('outFileName',varInputFileName)[0]

	## Engine
	# Gather Kpoint and Eigen Energy Information
	print 'Gathering Eigen System Data...'
	dBands = fGatherEigenData(inFileName,query)

	# Perform Projwfc.x Calculation
	# Do not Rerun projwfc.x if Output File Already Exists
	if (pwfcOutputFile not in os.listdir(os.getcwd())):
		print 'Running Projwfc.x...'
		fProjwfc(pwfcPath,pwfcOutputFile,pwfcOutputStd,pwfcInput)
	else:
		print pwfcOutputFile + ' File Already Exists...'

	# Gather Projected Wavefunction Data
	print 'Gathering Wavefunction Data...'
	wfcData = fGatherWfcData(pwfcOutputFile)

	# Find Swaps
	print 'Finding Swaps...'
	swaps = fFindSwaps(wfcData)

	# Repeat Cycle Until No More Swaps are Detected
	while (len(swaps) != 0):
		print 'Swap Cycle Number: ' + str(cycleNum)
		
		# Filter Swaps to Preserve Consistency
		print 'Filtering Swaps...'
		swaps = fFilterSwaps(swaps)
		
		# Perform Swap Operations
		print 'Swapping Bands...'
		dBands,wfcData = fSwap(swaps,dBands,wfcData)
		
		# Find Swaps
		print 'Finding Swaps...'
		swaps = fFindSwaps(wfcData)
		
		# Increment Cycle Number
		cycleNum += 1

	# Output to CSV File
	print 'Writing Output...'
	fOutput(outFileName,dBands)	
