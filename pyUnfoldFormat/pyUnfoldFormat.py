'''
pyUnfoldFormat.py

Author: Daniel Burrill
Date Created: August 20, 2014
Date Last Modified: August 21, 2014

v1.00
- Initial Build

Description:
 Works with unfold-x utility for Quantum Espresso. This script converts
 the binary output to double format, outputs to a file, and then plots
 the spectral functions after smoothing the data.
 
Future Improvements:
 This script was only tested with a graphene system. I am unsure how it
 will perform when bands are sorted by spin.
 
 NOTE: Smoothing kernel is crude. Change to fit preferences.
 
 THIS SCRIPT IS A HEAVILY MODIFIED VERSION OF THE TOOLS PROVIDED WITH
 UNFOLD-X AS OF AUGUST 21, 2014
 
'''

## Imports
import struct
import numpy
import matplotlib.pyplot
import scipy.interpolate
import scipy.signal

## Functions
def fUniqueVals(vector):
	'''
	Iterates through a given list and returns the number of unique
	elements.
	
	INPUT
		Input is a list (something iterable in 1d)
		
	OUTPUT
		Outputs the number (integer) of unique elements in 'vector'
	'''
	
	vals = []
	
	for element in vector:
		if (round(element,2) not in vals):
			vals.append(round(element,2))
	
	return len(vals)
	
## Main
if (__name__ == '__main__'):
	## Variables
	inFileName = 'graphene.dat'
	outFileName = 'graphene_formatted.dat'
	outFile = open(outFileName,'w')
	endian = '<'
	
	## Convert from binary to double and output to file
	with open(inFileName,'rb') as inFile:
		# Read first three 8-bit records
		fileContent=inFile.read(24)
		
		# As long as the record is not empty, unpack
		while fileContent:
			
			# Unpack the x,y,z (k,energy,spectral function value) values
			val = struct.unpack(endian+'ddd', fileContent)
			
			# Output as comma delimited
			outFile.write(str(val[0]) + ',' + str(val[1]) + ',' + str(val[2]) + '\n')
			
			# Read next three values
			fileContent = inFile.read(24)
			
	# Close inFile
	inFile.close()
	
	# Close outFile
	outFile.close()
	
	## Plot spectral function
	# Load data from file
	x,y,z = numpy.loadtxt(outFileName,delimiter=',',unpack=True)
	
	# Smooth data
	xVals = fUniqueVals(x)							# Amount of x values
	yVals = fUniqueVals(y)							# Amount of y values

	zShape = numpy.reshape(z,(xVals,yVals))			# Must be 2d
	
	smoothKernel = numpy.array([[0, 1, 0],
								[1, 1, 1],
								[0, 1, 0]]) 		# Convolution matrix
	
	zConv = scipy.signal.convolve2d(zShape, smoothKernel, mode='same')
	
	extent = [x.min(), x.max(), y.min(), y.max()]	# Define min and max
	
	# Plot
	matplotlib.pyplot.imshow(zConv.T,extent=extent,interpolation='gaussian',origin='lower',aspect='auto')
	
	# Show plots
	matplotlib.pyplot.show()
