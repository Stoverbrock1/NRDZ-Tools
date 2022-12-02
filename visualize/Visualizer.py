import numpy as np
import matplotlib.pyplot as plt
import sys
import os

### User-defined parameters:

WRITE_DATA = False # -w, -W
VISUALIZE = True # -v, -V
MODE = 'stats' # --mode=...
dt = .5 # In seconds; --dt=...
df = 1 # In MHz; --df=...
Fi = 0 # In MHz; --fi=...
Ff = 1400 # In MHz; --ff=...
Ti = 0
Tf = 0
SENSOR = 'gate' # --sensor=...

BASE_PATH = '/mnt/datab-netStorage-1G/data/'
SENSOR_PATH = {'CHIME':'', 'GATE':'HCRO-NRDZ-GATE/40.8169N121.4677W/hcro-rpi-002/32274CF/', 'NORTH':'',
    'NORTH-1740':'', 'ROOFTOP':'HCRO-NRDZ-Rooftop/40.8169N121.4677W/hcro-rpi-001/3227508/',
    'WEST-740':'HCRO-NRDZ-WEST-740/40.8169N121.4677W/hcro-rpi-004/323E369/'}
BRANCH_PATH = '/20/10/1/'

"""
#################################################################################################################
#################################################################################################################
"""

params = {"sensor":SENSOR, "mode":MODE, "dt":dt, "df":df, "fi":Fi, "ff":Ff, "ti":Ti, "tf":Tf}
flags = {"v":VISUALIZE, "w":WRITE_DATA}
valid_sensors = ["chime", "gate", "rooftop", "north-1740", "west-740", "north"]
valid_modes = ["stats", "power", "cadence"]




class dataManager:
    def __init__(self, sensor=SENSOR, mode=MODE, dT=dt, dF=df, ti=Ti, tf=Tf, fi=Fi, ff=Ff):
        self.sensor = sensor
        self.mode = mode
        self.dt = dT
        self.df = dF
        self.ti = ti
        self.tf = tf
        self.fi = fi
        self.ff = ff
        self.dataPath = BASE_PATH + SENSOR_PATH[sensor.upper()]

    def verify_parameters(self):
        """ Returns True if all parameters/arguments are valid """
        verified = True
        if ((self.mode not in valid_modes) or (self.sensor not in valid_sensors)):
            verified = False

        try:
            float(self.dt)
            float(self.df)
            float(self.ti)
            float(self.tf)
            float(self.fi)
            float(self.ff)
        except:
            verified = False

        if (verified):
            print("All parameters valid")

        else:
            print("Not all parameters valid")

        return verified


    def generate_spectrogram(self, save=False):
        """ Returns spectrogram data """
        return 0

    def plot_spectrogram(self, save=False):
        """ Plots spectrogram """
        return 0

    def generate_cadences(self, save=False):
        """ Returns sweep cadence data """
        tuples = []
        date = '0901'
        for directory in os.listdir(self.dataPath):
            if directory.isnumeric():
                for file in os.listdir(self.dataPath + directory + BRANCH_PATH):
                    if (file != "outputs"):
                        yearInd = file.index('D2022')
                        if (file[yearInd + 5: yearInd+9] == date):
                            indTime = float(file[yearInd + 10:yearInd+12]) + float(file[yearInd+12: yearInd + 14])/60.
                            tuples += [(indTime, float(directory))]

        sortT = [x[0] for x in tuples]
        unsortT = [x[0] for x in tuples]
        sortT.sort()
        unsortF = [x[1] for x in tuples]
        sortF = []
        for each in sortT:
            eachind = unsortT.index(each)
            sortF += [unsortF[eachind]]
            unsortT[eachind] = np.nan
        print(sortT)
        print("function was called")
        print(sortF)
        return [[sortT], [sortF]]

    def plot_cadences(self, save=False):
        """ Plots frequency sweep vs time """
        times, freqs = self.plot_cadences(save)
        plt.plot(times, freqs)
        return 0

    def generate_stats(self, save=False):
        """ Returns mean, min, max, and quartile data """
        return {}

    def plot_means(self, save=False):
        """ Plots means given this object's specified frequency/time bins """
        return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    pInd = 0
    while(pInd < len(args)):
        thisP = args[pInd]
        if ((thisP[:2] == "--") and ("=" in thisP)):
            P = thisP[2:thisP.index("=")].lower()
            if (P not in params):
                print("Please provide valid arguments")
                exit()
            pArg = thisP[thisP.index("=")+1:].lower()
            params[P] = pArg

        elif ((thisP[:1] == "-")):
            P = thisP[1:].lower()
            if (P not in flags):
                print("Unrecognized flag: " + thisP)
                exit()
            flags[P] = True
        else:
            print("Please provide valid arguments")
            exit()


        pInd += 1

    data = dataManager(params['sensor'], params['mode'], params['dt'], params['df'], params['ti'], params['tf'], params['fi'], params['ff'])
    print("SENSOR: " + data.sensor, "MODE: " + data.mode, "dt: " + str(data.dt), "df: " + str(data.df), "ti: " + str(data.ti), "tf: "+ str(data.tf), "fi: "+ str(data.fi), "ff: "+ str(data.ff))

    if (data.verify_parameters() == False):
        exit()

    if (data.mode == 'stats'):
        if (flags['w']):
            data.generate_stats(flags['w'])
        if (flags['v']):
            data.plot_means(flags['w'])

    if (data.mode == 'power'):
        if (flags['w']):
            data.generate_spectrogram(flags['w'])
        if (flags['v']):
            data.plot_spectrogram(flags['w'])

    if (data.mode == 'cadence'):
        if (flags['w']):
            data.generate_cadences(flags['w'])
        if (flags['v']):
            data.plot_cadences(flags['w'])
