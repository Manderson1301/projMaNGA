# to supress printing warnings to screen
import warnings
warnings.filterwarnings("ignore")

#import statements
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib import rc
import direcFuncs


def plotBPT(filename):

    temp = fits.open(filename)

    nFP = direcFuncs.setupNewDir(filename, "BPT", "")

    # for splitting the filename
    name = (filename.split('/')[-1]).split('.')[0]
    name_plateNum_Bundle = '-'.join(name.split('-')[1:3])

    # Taking data from GFlux
    headerInd = 1

    # extract OIII and make into 1D array
    OIII = temp[headerInd].data[3]
    OIII1D = OIII.reshape(1, OIII.size)

    # extract Hb and make into 1D array
    Hb = temp[headerInd].data[1]
    Hb1D = Hb.reshape(1, Hb.size)

    # extract NII and make into 1D array
    NII = temp[headerInd].data[6]
    NII1D = NII.reshape(1, NII.size)

    # extract Ha and make into a 1D array
    Ha = temp[headerInd].data[7]
    Ha1D = Ha.reshape(1, Ha.size)

    # plot
    logX = np.log(NII1D / Ha1D)
    logY = np.log(OIII1D / Hb1D)

    # removing large and small X values
    logX[abs(logX) > 20] = np.NaN

    # removing large and small Y values
    logY[abs(logY) > 20] = np.NaN

    # for demarkations
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    c = np.linspace(np.nanmin(logX) - 2, 2, 100)

    for i in c:
        if(i < 0.05):
            x1.append(i)
            y1.append(0.61 / (i - 0.05) + 1.3)
        if(i < .47 and i > -1.2805):
            x2.append(i)
            y2.append(0.61 / (i - 0.47) + 1.19)

    #plot and save
    plt.figure()
    plt.scatter(logX, logY)
    axes = plt.gca()
    xmin, xmax = axes.get_xlim()
    ymin, ymax = axes.get_ylim()

    x1_at_yHalf = np.argmin(abs(y1 - ymin / 2))
    x2_at_yHalf = np.argmin(abs(y2 - ymin / 2))

    plt.title("Spatially Resolved BPT Diagram -- " + name)
    plt.xlabel("log [NII]/H${\\alpha}$")
    plt.ylabel("log [OIII]/H${\\beta}$")
    plt.annotate('Sy', xy=((x1[x1_at_yHalf] + x2[x2_at_yHalf]) * 0.5,
                           (1.2 + ymax) / 2), size='18', color='r')
    plt.annotate('SF', xy=((x1[x1_at_yHalf] + xmin) * 0.8,
                           ymin / 2), size='18', color='m')
    plt.annotate('Inter', xy=((x1[x1_at_yHalf] + x2[x2_at_yHalf])
                              * 0.5, ymin / 2), size='12', color='g')
    plt.plot(x1, y1, 'k')
    plt.plot(x2, y2, '--k')
    plt.xlim([xmin, xmax])
    plt.ylim([ymin, ymax])
    plt.savefig(nFP + name_plateNum_Bundle + '_BPT.png')
    # plt.show()
    plt.close()
