import numpy as np

from astropy.io.fits.verify import VerifyError, VerifyWarning
import matplotlib.pyplot as plt

import string

import direcFuncs as dF
import plottingTools as pT
import plotFuncs as pF
from GalaxyObject import fitsExtraction as fE

from plotSFH import plotSFH


def plotPIPE3D(filepath, plotType, hdu):
    EADir, filename = dF.getEADirAndFilename(filepath)

    if plotType == 'sfh':
        plotSFH(filepath, filename, EADir, hdu)
    else:
        if plotType == 'flux_elines':
            if not filename.startswith(plotType):
                print("No plots of type (" + plotType + ") to make for the file " + filename)
                return
        if plotType == 'indices.cs':
            if not filename.startswith(plotType[:7]):
                print("No plots of type (" + plotType + ") to make for the file " + filename)
                return
        plate_IFU = fE.pullPLATEIFU(hdu[0].header, filename)
        Re = fE.getRe(EADir, plate_IFU)

        center = 'HEX'

        NAXIS3 = fE.getNAXIS3(hdu)

        titleHdr = fE.getTitleHeaderPrefix(hdu)

        dataInd = 0

        dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair = createDictionaries(
            hdu, NAXIS3, titleHdr, dataInd, filename)

        if plotType == 'requested':
            requestedWithin = [['velocity', 'stellar population'], ['Ha'], ['Hd'], ['Halpha']]

            dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair = removeNonRequested(
                dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair, requestedWithin)

            nFP = dF.assure_path_exists(EADir + '/PLOTS/PIPE3D/' + plotType + '/' + plate_IFU + '/')
            nFPraw = ''
        else:
            nFP = dF.assure_path_exists(EADir + '/PLOTS/PIPE3D/' + plate_IFU + '/' + plotType + '/')
            nFPraw = dF.assure_path_exists(EADir + '/PLOTS/PIPE3D/' + plate_IFU + '/' + plotType + '/RAW/')

        if not bool(dictPlotTitles_Index):
            print("No plots of type (" + plotType + ") to make for the file " + filename)
            return
        elif nFPraw != '':
            hex_at_Cen, gal_at_Cen = fE.getCenters(hdu, plate_IFU, dataInd)
            for key in dictPlotTitles_Index.keys():
                if key in dictPlotTitles_Error.values():
                    continue
                dataMat, maskMat, newFileName, plotTitle, units = prepData(
                    dictPlotTitles_Index, key, hdu, filename, plate_IFU, dataInd, NAXIS3)
                if dataMat is None:
                    continue
                aspectRatio = 16.0 / 13
                height = 10
                fig = plt.figure(figsize=(aspectRatio * height, height))
                plt.suptitle(plate_IFU + " :: " + newFileName)
                axes = plt.gca()
                pF.spatiallyResolvedPlot(axes,
                                         plotType,
                                         newFileName,
                                         hdu,
                                         plate_IFU,
                                         dataInd,
                                         Re,
                                         gal_at_Cen,
                                         hex_at_Cen,
                                         dataMat,
                                         maskMat,
                                         center,
                                         units,
                                         None,
                                         None)
                # fig.tight_layout()
                # plt.show()
                # print(jello)
                plt.savefig(nFPraw + newFileName + '.png')
                # print(jello)
                plt.close()

        if bool(dictPlotTitles_Error):
            for key in dictPlotTitles_Error.keys():
                dataMat, maskMat, newFileName, plotTitle, units = prepData(
                    dictPlotTitles_Index, key, hdu, filename, plate_IFU, dataInd, NAXIS3)
                if dataMat is None:
                    continue
                keyOfError = dictPlotTitles_Error[key]
                errMat = hdu[dataInd].data[dictPlotTitles_Index[keyOfError]]
                pF.plotQuadPlot(hdu,
                                dataInd,
                                plate_IFU,
                                center,
                                plotTitle,
                                nFP,
                                newFileName,
                                EADir,
                                Re,
                                dataMat,
                                maskMat,
                                errMat,
                                units,
                                vmin=None,
                                vmax=None)

        if bool(dictPlotTitles_Pair):
            for key in dictPlotTitles_Pair.keys():
                dataMat1, maskMat1, newFileName1, plotTitle1, units1 = prepData(
                    dictPlotTitles_Index, key, hdu, filename, plate_IFU, dataInd, NAXIS3)
                dataMat2, maskMat2, newFileName2, plotTitle2, units2 = prepData(
                    dictPlotTitles_Index, dictPlotTitles_Pair[key], hdu, filename, plate_IFU, dataInd, NAXIS3)
                if dataMat1 is None or dataMat2 is None:
                    continue
                pF.plotComparisonPlots(hdu,
                                       plate_IFU,
                                       dataInd,
                                       nFP,
                                       EADir,
                                       plotType,
                                       newFileName1,
                                       newFileName2,
                                       Re,
                                       dataMat1,
                                       maskMat1,
                                       dataMat2,
                                       maskMat2,
                                       hex_at_Cen,
                                       gal_at_Cen,
                                       center,
                                       units1,
                                       units2)


def prepData(titleDict, key, hdu, filename, plate_IFU, dataInd, NAXIS3):
    if NAXIS3 == 0:
        dataMat = hdu[dataInd].data
        newFileName = filename
    else:
        dataMat = hdu[dataInd].data[titleDict[key]]
        newFileName = key

    maskMat = np.zeros(dataMat.shape)
    maskMat[dataMat == 0] = 1
    maskMat[np.abs(dataMat) > 30000] = 1

    plotTitle = plate_IFU + " :: " + newFileName

    if not filename.startswith('flux_elines') and not filename.startswith('indices'):
        if titleDict[key] > 99:
            units = hdu[dataInd].header["UNITS_" + str(99)]
        else:
            units = hdu[dataInd].header["UNITS_" + str(titleDict[key])]
        units = units.strip()
        if units == 'yr':
            units = 'log(Age(Gyr))'
            dataMat = np.log10(dataMat)
        elif units == 'Solar metallicity':
            units = '[Z/H]'

        if units == 'km':
            units = 'km/s'

        if 'mass weighted' in newFileName:
            units = units + '_{MW}'
        elif 'luminosity weighted' in newFileName:
            units = units + '_{LW}'

        units = '$' + units + '$'
    else:
        units = ""

    newFileName = newFileName.strip()
    newFileName = string.capwords(newFileName)

    return dataMat, maskMat, newFileName, plotTitle, units


def removeNonRequested(dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair, requestedWithin):
    for key in dictPlotTitles_Index.keys():
        flag = False
        for withinTextVec in requestedWithin:
            currFlag = True
            for withinComponent in withinTextVec:
                if not flag and withinComponent not in key:
                    currFlag = False
            if currFlag:
                flag = True
        if not flag:
            del dictPlotTitles_Index[key]
            if key in dictPlotTitles_Error.keys():
                del dictPlotTitles_Error[key]
            if key in dictPlotTitles_Pair.keys():
                del dictPlotTitles_Pair[key]
    return dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair


def createDictionaries(hdu, NAXIS3, titleHdr, dataInd, filename):
    dictPlotTitles_Index = {}
    dictPlotTitles_Error = {}
    dictPlotTitles_Pair = {}

    for i in range(NAXIS3):
        try:
            plotTitle = hdu[dataInd].header[titleHdr + str(i)]
            plotTitle = plotTitle.strip()
            dictPlotTitles_Index[plotTitle] = i
        except VerifyError:
            print('The header title ' + titleHdr + str(i) + ' is corrupt for the file ' + filename)
            continue

    errorPrefixes = ['e_', 'error in the ', 'error of the ', 'error of ', 'error in ', 'error ']
    pairSuffixes = ['weighted metallicity of the stellar population', 'weighted age of the stellar population', ]
    pairFlagsFirstFound = [False, False]
    pairFlagsSecondFound = [False, False]
    tempPairKey = ['', '']

    for key in dictPlotTitles_Index.keys():
        for errorPrefix in errorPrefixes:
            if errorPrefix in key:
                TitleFromWhereErrorBelongs = key[len(errorPrefix):]
                if TitleFromWhereErrorBelongs in dictPlotTitles_Index.keys():
                    dictPlotTitles_Error[TitleFromWhereErrorBelongs] = key
                else:
                    for key2 in dictPlotTitles_Index.keys():
                        if key != key2 and key2.endswith(TitleFromWhereErrorBelongs):
                            dictPlotTitles_Error[key2] = key
                break

        for i in range(len(pairSuffixes)):
            pairSuffix = pairSuffixes[i]
            if not pairFlagsFirstFound[i] and key.endswith(pairSuffix):
                tempPairKey[i] = key
                pairFlagsFirstFound[i] = True
            elif not pairFlagsSecondFound[i] and key.endswith(pairSuffix):
                # print(str(i) + " " + str(pairFlagsSecondFound[i]))
                dictPlotTitles_Pair[tempPairKey[i]] = key
                pairFlagsSecondFound[i] = True

    return dictPlotTitles_Index, dictPlotTitles_Error, dictPlotTitles_Pair
