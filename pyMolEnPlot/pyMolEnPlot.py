'''
pyMoleEnPlot.py

Author: Daniel Burrill
Date Created: September 24, 2013
Date Last Modified: October 12, 2013

v1.02
- Added data output
- Fixed scaling with multiple k points/spin

v1.01
- Swapped axes
- Generalized for multiple columns

v1.00
- Initial Build

Description:
 Plots the molecular energy levels and UPS spectra from csv file. The input file
 works best when taken from pyQEEig. Uses superposition of Guassians to create
 UPS data.
 
 !!!!!NOT GENERALIZED YET!!!!!
 - Will add a format file to adjust graphing parameters
 
'''

# Imports
import pylab

# Variables
inFile = 'Eigs.csv'
lineWidth = 1
offset = 10
outFile = 'IntensityData'
sFE = True                  # Switch for specifying Fermi Energy
fermiEnergy = -4.19

# UPS Variables
gWidth = 0.7
gamma = (gWidth*gWidth)/(4*pylab.log(2))
energyRange = [-30,5]
IVal = []
TotalInt = []

# Font Dictionary
fontDictionary = {'horizontalalignment':'center',
                  'fontsize':16}
                  
# Functions

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
                  
if __name__ == '__main__':
    # Load csv Data
    enData = pylab.loadtxt(inFile,delimiter=',')
    
    # Calculate UPS
    # Single k-point
    if (len(pylab.shape(enData)) == 1):
        for energy in enData:
            eigFunc = []
            
            for energyVal in pylab.arange(energyRange[0],energyRange[1],step=0.01):
                enCalc = pylab.exp(-((energyVal-float(energy))*(energyVal-float(energy)))/(gamma))
                eigFunc.append(enCalc)
                
            IVal.append(eigFunc)
            
        # Total Intensity
        for eigEn in pylab.transpose(IVal):
            TotalInt.append(pylab.sum(eigEn))
            
        # Normalize Total Intensity
        
        # Plot Energy Levels
        energyGraph = pylab.subplot(2,1,2)
        for energy in enData:
            pylab.vlines(energy,offset,offset+lineWidth)
            
        pylab.xlabel('Energy (eV)')
        pylab.xlim((energyRange[0],energyRange[1]))
        energyGraph.axes.get_yaxis().set_visible(False)
            
        # Plot UPS Spectra
        xVal = pylab.arange(energyRange[0],energyRange[1],step=0.01)
        spectraGraph = pylab.subplot(2,1,1)
        pylab.plot(xVal,TotalInt)
        pylab.title('Calculated UPS Spectra')
        pylab.xlim((energyRange[0],energyRange[1]))
        pylab.ylim((0,max(TotalInt)))
        spectraGraph.axes.get_yaxis().set_visible(False)
        spectraGraph.axes.get_xaxis().set_visible(False)
        
        # Fermi Energy Line
        pylab.vlines(fermiEnergy,0,max(TotalInt),linestyles='--')
        
        # Output Data
        tempStr = ''
        oFile = open(outFile + '.csv', 'w')
            
        for index2,intensity in enumerate(TotalInt):
            tempStr = str(xVal[index2]) + ',' + str(intensity) + '\n'
            oFile.write(tempStr)
            
        oFile.close()
    
    # More than one energy column
    else:
        for index,kpoint in enumerate(pylab.transpose(enData)):
            pylab.figure(index)
            IVal = []
            TotalInt = []
            
            # Create Gaussians
            for energy in kpoint:
                eigFunc = []
            
                for energyVal in pylab.arange(energyRange[0],energyRange[1],step=0.01):
                    enCalc = pylab.exp(-((energyVal-float(energy))*(energyVal-float(energy)))/(gamma))
                    eigFunc.append(enCalc)
                    
                IVal.append(eigFunc)
            
            # Total Intensity
            for eigEn in pylab.transpose(IVal):
                TotalInt.append(pylab.sum(eigEn))
                
            # Normalize Total Intensity
            
            # Plot Energy Levels
            energyGraph = pylab.subplot(2,1,2)
            for energy in kpoint:
                pylab.vlines(energy,offset,offset+1)
                
            pylab.xlim((energyRange[0],energyRange[1]))
                
            pylab.xlabel('Energy (eV)')
            energyGraph.axes.get_yaxis().set_visible(False)
                
            # Plot UPS Spectra
            xVal = pylab.arange(energyRange[0],energyRange[1],step=0.01)
            spectraGraph = pylab.subplot(2,1,1)
            pylab.plot(xVal,TotalInt)
            pylab.xlim((energyRange[0],energyRange[1]))
            pylab.ylim((0,max(TotalInt)))
            pylab.title('Calculated UPS Spectra')
            spectraGraph.axes.get_yaxis().set_visible(False)
            spectraGraph.axes.get_xaxis().set_visible(False)
            
            # Fermi Energy Line
            pylab.vlines(fermiEnergy,0,max(TotalInt),linestyles='--')
            
            # Output Data
            tempStr = ''
            oFile = open(outFile + str(index) + '.csv', 'w')
                
            for index2,intensity in enumerate(TotalInt):
                tempStr = str(xVal[index2]) + ',' + str(intensity) + '\n'
                oFile.write(tempStr)
                
            oFile.close()
            
    # Show Plots
    pylab.show()