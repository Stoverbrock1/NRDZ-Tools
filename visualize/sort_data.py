import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime, timedelta
import re
import plots
import check_list

# days must be in MM/DD/YYYY string
days = ['08/07/2022']
# days = ['07/15/2022', '07/16/2022', '07/17/2022', '07/18/2022', '07/19/2022',
#         '07/20/2022', '07/21/2022', '07/22/2022', '07/23/2022', '07/24/2022',
#         '07/25/2022']
freqs = np.linspace(410, 1790, 70, dtype=int)

nrdz_dict = {
    'rooftop': ['HCRO-NRDZ-Rooftop', 'hcro-rpi-001', '3227508'],
    # 'gate': ['HCRO-NRDZ-Gate', 'hcro-rpi-002', '32274CF'],
    'chime': ['HCRO-NRDZ-CHIME', 'hcro-rpi-003', '3227512'],
    'gate': ['HCRO-NRDZ-GATE', 'hcro-rpi-002', '32274CF'],
    'north1740': ['HCRO-NRDZ-NORTH-1740', 'hcro-rpi-005', '32274A4'],
    'west740': ['HCRO-NRDZ-WEST-740', 'hcro-rpi-004', '323E369']
}

base_dir = os.path.join(os.sep, 'mnt', 'datab')
nrdz_dirs = []
for place in nrdz_dict:
    directory = os.path.join(base_dir, 'data',
                        nrdz_dict[place][0], '40.8169N121.4677W', nrdz_dict[place][1],
                        nrdz_dict[place][2])
    nrdz_dirs.append(directory)

plots_dir = os.path.join(base_dir, 'visualize', 'plots')
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# location_dir_list = []

for day in days:
    day_formatted = datetime.strptime(day, '%m/%d/%Y').strftime('%Y%m%d')
    for path in nrdz_dirs:
        empty_frs = [] # record frequencies with no data for given day and sensor
        good = True

        # create path to sensor directories in plots directory
        split_path = os.path.normpath(path).split(os.sep)
        location = split_path[4]
        location_dir = os.path.join(plots_dir, location)
        # location_dir_list.append(os.path.join(plots_dir, location))

        for fr in freqs:
            # create path to frequency directory within each plot and sensor path
            plotshere_dir = os.path.join(plots_dir, location, str(fr))
            if not os.path.exists(plotshere_dir):
                os.makedirs(plotshere_dir)

            # grab files from one day from one frequency
            freq_dir = os.path.join(path, str(fr), '20', '10', '1')
            file_list = glob.glob(os.path.join(freq_dir, '*D'+day_formatted+'*.sc16'))
            if len(file_list) == 0:
                empty_frs.append(fr)

            # create spectrogram, histogram, and PSD for each file
            plots.create_plots(plotshere_dir, file_list, day_formatted)

        if len(empty_frs) > 0:
            print('No data found for '+day+' in '+path+' at freqs '+str(empty_frs))
            if len(empty_frs)==len(freqs):
                good = False

        # collect flagged files with errors from one day and plot them
        # only goes if data collected at all frequencies with all sensors
        if good:
            print('Visualizing files with errors in '+location_dir+' on '+day+'...')
            big_check_path = check_list.large_check_list(location_dir, freqs, day_formatted) # generate file with all errors from one day
            check_list.clean_check_list(big_check_path) # in case old path dirs in there, clean up
            plots.passfail_plot(location_dir, freqs, day_formatted)
            print('Complete')
        
