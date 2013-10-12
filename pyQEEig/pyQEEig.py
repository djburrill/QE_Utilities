"""
pyQEEig.py

Author: Daniel Burrill
Date Created: September 25, 2013
Date Last Modified: September 25, 2013

v1.00
- Initial Build

Description:
 Pulls k-point energy eigenvalues from output file of QE. Outputs to csv file
 where each column represents the eigenvalues of a single k-point. Spin 
 separated k-points are not labeled as such (yet).
 
"""

# Variables
fileName = 'output.out'
catchCont = ['k','=','bands']
dataCont = []
kCont = []
switch = False
outFile = 'Eigs.csv'

# Functions

# Main
if (__name__ == '__main__'):
    # Open File
    fileCont = open(fileName,'r')
    
    # Parse Through fileCont Looking for catchStr
    for line in fileCont:
	# Remove White Space Padding
	line = line.strip()
	
	# Separate Words by Spaces
	line = line.split()

	# Stop Recording if End of Block is Reached
	if (line == []) and (switch == True) and (len(kCont) != 0):
	   switch = False
	   dataCont.append(kCont)
	   kCont = []

	# Record Lines in Specified Zone
	if (switch == True):
	   kCont.extend(line)

	# Check line Against catchCont
	catch = 0
	for catchWord in catchCont:
	    if (catchWord in line):
	        catch += 1
	        
	if (catch == len(catchCont)) and (switch == False):
	   switch = True

    # Close fileCont and Open outFile
    fileCont.close()
    oFile = open(outFile, 'w')
    
    # Write Data to csv
    
    # Write Header
    tempStr = '# '
    for index,kPoint in enumerate(dataCont):
        if (index == len(dataCont)-1):
            tempStr += 'KPoint ' + str(index) + '\n'
        else:
            tempStr += 'KPoint ' + str(index) + ','
            
    oFile.write(tempStr)
            
    # Write Data
    for index,eEig in enumerate(dataCont[0]):
        tempStr = ''
        for index2,kPoint in enumerate(dataCont):
            if (index2 == len(dataCont)-1):
                tempStr += kPoint[index] + '\n'
            else:
                tempStr += kPoint[index] + ','
                
        oFile.write(tempStr)
        
    # Close oFile
    oFile.close()
        
    