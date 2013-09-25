"""
pyMoleEnPlot.py

Author: Daniel Burrill
Date Created: September 24, 2013
Date Last Modified: September 24, 2013

v1.00
- Initial Build

Description:
 Plots the molecular energy levels and UPS spectra from csv file. The input file
 works best when taken from pyQEEig. Uses superposition of Guassians to create
 UPS data.
 
 !!!!!NOT GENERALIZED YET!!!!!
 - Will add a format file to adjust graphing parameters
 
"""

# Imports
import pylab

# Variables
inFile = 'data.csv'
lineWidth = 1
offset = 10

# UPS Variables
gWidth = 0.7
gamma = (gWidth*gWidth)/(4*pylab.log(2))
energyRange = [-30,0]
IVal = []
TotalInt = []

# Font Dictionary
fontDictionary = {'horizontalalignment':'center',
                  'fontsize':16}
                  
if __name__ == '__main__':
    # Load csv Data
    enData = pylab.loadtxt(inFile,delimiter=',')
    
    # Calculate UPS
    for energy in enData:
        eigFunc = []
        
        for energyVal in pylab.arange(energyRange[0],energyRange[1],step=0.01):
            enCalc = pylab.exp(-((energyVal-float(energy))*(energyVal-float(energy)))/(gamma))
            eigFunc.append(enCalc)
            
        IVal.append(eigFunc)
        
    # Total Intensity
    for eigEn in pylab.transpose(IVal):
        TotalInt.append(pylab.sum(eigEn))
    
    # Plot Energy Levels
    energyGraph = pylab.subplot(1,2,1)
    for energy in enData:
        pylab.hlines(energy,offset,offset+lineWidth)
        
    pylab.title('Calculated H2Pc Energy Levels')
    pylab.ylabel('Energy (eV)')
    energyGraph.axes.get_xaxis().set_visible(False)
        
    # Plot UPS Spectra
    spectraGraph = pylab.subplot(1,2,2)
    pylab.plot(TotalInt,pylab.arange(energyRange[0],energyRange[1],step=0.01))
    pylab.title('Calculated UPS Spectra')
    spectraGraph.axes.get_yaxis().set_visible(False)
    spectraGraph.axes.get_xaxis().set_visible(False)
        
    # Show Plots
    pylab.show()