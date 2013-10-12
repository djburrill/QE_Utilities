'''
pyExprPlot.py

Author: Daniel Burrill
Date Created: October 7, 2013
Date Last Modified: October 12, 2013

v1.00
- Initial Build

Description:
 Plots the experimental and theorectical UPS spectra. Allows manipulation
 of plots for better visualization
 
 !!!!!NOT GENERALIZED YET!!!!!
 - Will add a format file to adjust graphing parameters
 
'''

# Imports
import pylab

# File Variables
dataFiles = ['Files','File2']
dataLabels = ['Labels','Label2']

# Data Adjustments
dataShifts = [(3.7,0),(3.7,0)]
dataScale = [1.4,1.4]

# Containers
dataCont = []

# Font Dictionary
fontDictionary = {'horizontalalignment':'center',
                  'fontsize':16}
                  
# Functions
def ElementShift(vector,shift):
    for index,element in enumerate(vector):
        vector[index] = element+shift
        
    return vector
    
def Normalize(vector):
    maxVal = 0
    
    # Find Maximum
    for index,element in enumerate(vector):
        if (element > maxVal):
            maxVal = element
            
    # Normalize
    for index,element in enumerate(vector):
        vector[index] = element/maxVal
        
    return vector
    
def Scale(vector,scale):    
    for index,element in enumerate(vector):
        vector[index] = element*scale    
    
    return vector
                  
# Main
if (__name__ == '__main__'):
    ## Load csv Data
    for name in dataFiles:
        dataCont.append(pylab.transpose(pylab.loadtxt(name,delimiter=',')))
        
    ## Normalize Y Values
    for index,data in enumerate(dataCont):
        dataCont[index][1] = Normalize(data[1])
    
    ## Plot Adjustments
    # Coordinate Shift
    for index,data in enumerate(dataCont):
        dataCont[index][0] = ElementShift(data[0],dataShifts[index][0])
        dataCont[index][1] = ElementShift(data[1],dataShifts[index][1])
        
    # Scale
    for index,data in enumerate(dataCont):
        dataCont[index][0] = Scale(data[0],dataScale[index])
    
    ## Plot
    # Initialize Plot
    for index,data in enumerate(dataCont):
        pylab.plot(data[0],data[1],label=dataFiles[index])
    
    # Plot Labels
    pylab.xlabel('Energy (eV)')
    pylab.ylabel('Intensity (arb. units)')
    pylab.title('Theoretical & Experimental')
    pylab.legend(dataLabels,loc=2)
    
    ## Special Changes (Remember to remove after each data set)
    # Fermi Energy
    fermiEnergy = (0+3.7)*1.4
    pylab.vlines(fermiEnergy,0,2,linestyles='--')
    
    pylab.show()