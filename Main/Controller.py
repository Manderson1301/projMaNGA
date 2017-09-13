'''
Created on Sep 8, 2017

@author: Mande
'''
import numpy as np
from Utilities.Stopwatch import Stopwatch
from collections import defaultdict
import Utilities.direcFuncs as dF
from astropy.io import fits
from GalaxyObject.Galaxy import Galaxy
from PlottingDrivers.plottingController import plottingController
import os


class Controller:

    resourceFolder = os.path.join(os.path.abspath(
        os.path.join(__file__, "..", "..")), "resources")

    dictMPL4files = eval(
        open(os.path.join(resourceFolder, "dictMPL4files.txt")).read())
    dictMPL5files = eval(
        open(os.path.join(resourceFolder, "dictMPL5files.txt")).read())
    dictPIPE3Dfiles = eval(
        open(os.path.join(resourceFolder, "dictPIPE3Dfiles.txt")).read())

    def __init__(self, args):
        self.inputs = args

    def run(self):
        opts, EADirectory = self.obtainUserOptsInput()
        # EADirectory - where all plots and data are saved
        # opts - the arguments following the run command that dictate what
        # plots the user wants to produce
        print("")
        print('The program will search this directory for .fits and .fits.gz files:')
        print('     ' + EADirectory)
        print("")
        print()
        timer = Stopwatch()
        timer.start()
        fileDict = self.requiredFileSearch(opts, EADirectory)
        if not fileDict:
            print("")
            print(
                r"No files were found in the directory supplied. The program will now close. Avoiding ending the directory with the character '\' and put the entire directory in quotes if there are any spaces in the path")
            print("")
            timer.stop()
        else:
            print("")
            print('The program found this many .fits and .fits.gz files:  ' +
                  str(len(fileDict.items())))
            print("")
            self.makePLOTS(fileDict, opts, EADirectory)
            timer.stop()
            timer.reportDuration()

    def obtainUserOptsInput(self):
        opts = []
        try:
            EADirectory = self.inputs[1]
            del self.inputs[:2]
            for user_input in self.inputs:
                opts.append(user_input)
        except IndexError:
            print("No extra arguments supplied")
        except ValueError:
            # opts = initiateUserInterface()
            print("no user interface built")

        opts = [opt.lower() for opt in opts]
        return opts, os.path.normpath(EADirectory)

    def requiredFileSearch(self, opts, EADirectory):
        fileDict = defaultdict(list)
        if 'mpl4' in opts:
            fileDict.update(self.makeFilePlotDict(
                opts, os.path.join(EADirectory, "MPL-4", "DATA", "DAP"), self.dictMPL4files))
            if 'pipe3d' in opts:
                fileDict.update(self.makeFilePlotDict(
                    opts, os.path.join(EADirectory, "MPL-4", "DATA", "PIPE3D"), self.dictPIPE3Dfiles))
        if 'mpl5' in opts:
            fileDict.update(self.makeFilePlotDict(
                opts, os.path.join(EADirectory, "MPL-5", "DATA", "DAP"), self.dictMPL5files))
            # if 'pipe3d' in opts:
            #    fileDict.update(self.makeFilePlotDict(
            # opts, EADirectory + "MPL-5\\DATA\\PIPE3D\\",
            # self.dictPIPE3Dfiles))

        return fileDict

    def makeFilePlotDict(self, opts, EADirectory, dictFileTypes):
        filePlotDict = defaultdict(list)
        for key in dictFileTypes.keys():
            if key in opts:
                fileType = dictFileTypes[key]
                fileList = dF.locate(fileType, True, rootD=EADirectory)
                fileList_gz = dF.locate(
                    fileType + '.gz', True, rootD=EADirectory)
                fileList_gz = [
                    x for x in fileList_gz if x[:-3] not in fileList]
                fileList = np.append(fileList, fileList_gz)
                for file in fileList:
                    filePlotDict[file].append(key)
        return filePlotDict

    def makePLOTS(self, fileDict, opts, EADirectory):
        for fileItemPair in fileDict.items():
            file = fileItemPair[0]
            print("")
            print('File:')
            print('     ' + file)
            print('Plots to create:')
            print('     ' + str(fileItemPair[1]))
            print("")

            galaxy = Galaxy(file, fits.open(file))
            plotsToBeCreated = fileItemPair[1]
            myPlottingController = plottingController(
                EADirectory, galaxy, plotsToBeCreated, opts)
            myPlottingController.run()
            galaxy.close()
