# The data can be loaded with:
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
import re
from matplotlib import colors
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patches as mpatches
import glob
# from scipy.ndimage.filters import uniform_filter1d

def remove_suffix(input_string, suffix):
    '''
    from python3.9 docs, manually defined here for older versions
    '''
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def plot_spectrogram(filepath, data_complex, nfft, sampling_rate, center_frequency, std_width=6, show=False):
    '''
    Plots spectrogram and saves image. Variables past data_complex should come from .json file
    '''   
    plt.figure(figsize=(6,4))

    spec, freqs, t, im = plt.specgram(data_complex, NFFT=nfft, Fs=sampling_rate, Fc=center_frequency, 
                                        mode='psd', cmap='viridis')    
    
    # set colorbar range to be +/- [std_width] of mean
    std_width = std_width
    intensity = 10.0 * np.ma.log10(spec)
    vmin = (intensity.mean() - std_width*intensity.std())
    vmax = (intensity.mean() + std_width*intensity.std())
    im.set_clim(vmin=vmin, vmax=vmax)

    plt.colorbar(label='PSD (dB/Hz)')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()

def plot_histogram(filepath, data, std_width=6, show=False):
    '''
    asdfasfs
    '''
    plt.figure(figsize=(5, 4))
    plt.hist(data, bins=100)

    # calculate xlim
    std_width = std_width
    if std_width*data.std() > 2**15:
        xmin = -2**15
        xmax = 2**15
    else:
        xmin = (data.mean() - std_width*data.std())
        xmax = (data.mean() + std_width*data.std())
    plt.xlim(xmin, xmax)

    plt.xlabel('ADC Integer Value')
    plt.ylabel('Counts')
    plt.savefig(filepath, dpi=300)
    if show:
        plt.show()
    plt.close()


def plot_PSD(filepath, data_complex, nfft, sampling_rate, center_frequency, show=False):
    '''
    asdfasdfasfsa
    '''
    plt.figure(figsize=(6, 3))
    window = lambda data: data*np.hamming(len(data))
    plt.psd(data_complex, NFFT=nfft, Fs=sampling_rate, Fc=center_frequency, window=window)
    plt.xlim(center_frequency-sampling_rate/2, center_frequency+sampling_rate/2)
    plt.xlabel('Frequency (Hz)')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()


def get_data(sc16_file):
    '''
    asdfsfdf
    '''
    # get data from .sc16 file
    data = np.fromfile(sc16_file, np.int16)
    data_normalized = data / 32768                                          # 16 bit signed integer -> 1 bit sign, 15 bits data, 2^15 = 32678
    data_complex = data_normalized[0::2] + 1j*data_normalized[1::2]         # converts the data from IQIQIQ to I+jQ, I+jQ, I+jQ, ...

    # get header-type info from corresponding .json file
    file_beginning = remove_suffix(sc16_file, '.sc16')
    with open(file_beginning + '.json', 'r') as f:
        header = json.load(f)

    return data, data_complex, file_beginning, header


def create_plots(base_dir, sc16_list, day, plotspec=True, plotPSD=True, plothist=True):
    '''
    asdweews
    '''
    plot_dirs = ['spectrograms', 'histograms', 'PSDs']
    for dir in plot_dirs:
        newpath = os.path.join(base_dir, dir)
        if not os.path.exists(newpath):
            os.makedirs(newpath)

    checkfile_path = os.path.join(base_dir, day+'.txt')  # put the bad guys in here
    # open(checkfile_path, 'w').close() # clear bad guys on restart

    i = 0
    for sc16_file in sc16_list:
        i += 1
        print('###########################################')
        print('Checking '+str(i)+'/'+str(len(sc16_list))+' files...')

        data, data_complex, file_beginning, header = get_data(sc16_file)

        #############
        # bit check #
        #############
        if any(x in data for x in [1, 2, 3]):
            try:
                with open(checkfile_path) as f:
                    openfile = f.read()
            except:
                with open(checkfile_path, 'a') as f:
                    f.write(sc16_file + '\n')
            else:
                if sc16_file not in openfile:
                    with open(checkfile_path, 'a') as f:
                        f.write(sc16_file + '\n')
            print('FAIL: bit check')
        else:
            print('PASS: bit check')
        
        ####################################
        # integer count distribution check #
        ####################################
        if abs(data.mean()) > 1:
            try:
                with open(checkfile_path) as f:
                    openfile = f.read()
            except:
                with open(checkfile_path, 'a') as f:
                    f.write(sc16_file + '\n')
            else:
                if sc16_file not in openfile:
                    with open(checkfile_path, 'a') as f:
                        f.write(sc16_file + '\n')
            print('FAIL: integer count distribution check')
        else:
            print('PASS: integer count distribution check')

        #################################
        # simple matplotlib spectrogram #
        #################################
        sampling_rate = header['sampling_rate'] # integer value, e.g. 20000000 for 20 MS/s - required -> length of the sample is calculated with this
        center_frequency = header['frequency'] # integer value, e.g. 410000000 for 410 MHz - optional -> just for y-axis display, has no effect on the sample itself
        nfft = 1024 # ideally a multiple of 2, e.g. 512, 1024, 2048, etc.
        
        spec_path = os.path.join(base_dir, plot_dirs[0], os.path.basename(file_beginning)+'.png')
        if os.path.isfile(spec_path):
            if plotspec:
                plot_spectrogram(spec_path, data_complex, nfft, sampling_rate, center_frequency, std_width=6)
            else:
                # plot_spectrogram(spec_path, data_complex, nfft, sampling_rate, center_frequency, std_width=6)
                pass
        else:
            plot_spectrogram(spec_path, data_complex, nfft, sampling_rate, center_frequency, std_width=6)

        #####################################
        # histogram to check integer values #
        #####################################
        hist_path = os.path.join(base_dir, plot_dirs[1], os.path.basename(file_beginning)+'.png')
        if os.path.isfile(hist_path):
            if plothist:
                plot_histogram(hist_path, data)
            else:
                pass
        else:
            plot_histogram(hist_path, data)

        ##################################
        #            PSD plot            #
        ##################################
        PSD_path = os.path.join(base_dir, plot_dirs[2], os.path.basename(file_beginning)+'.png')
        if os.path.isfile(PSD_path):
            if plotPSD:
                plot_PSD(PSD_path, data_complex, nfft, sampling_rate, center_frequency)
            else:
                pass
        else:
            plot_PSD(PSD_path, data_complex, nfft, sampling_rate, center_frequency)


# need to pass in ONE DAY at a time
def passfail_array(freqs, bins):
    '''
    generate blank array of zeros based on frequency/time span
    dir: path to one of the three sensor directories
    '''
    y_span = len(freqs)

    # count number of plots produced in one folder --> # of 700s intervals
    x_span = len(bins)

    pf_array = np.zeros((x_span, y_span))
    # pf_array = np.full((x_span, y_span), -1)

    return pf_array


def get_datetime(file_path, file_end='.sc16'):
    '''
    asfsdfafds
    '''
    file = os.path.basename(file_path)
    strip_date = re.sub(r'^.*?D', 'D', file)
    obs_time = datetime.strptime(strip_date, 'D%Y%m%dT%H%M%SM%f'+file_end)

    return obs_time


def start_times(dir, freqs, day):
    '''
    for x-axis labelling
    dir: path to one of the three sensor directories
    '''
    # freq_dir = os.path.join(dir, str(freqs[0]), 'PSDs') # can use hist or spec directory too, just shorter name
    file_list = glob.glob(os.path.join(dir, str(freqs[0]), 'PSDs', '*'+day+'*'))
    time_list = []
    for file in file_list:
        time = get_datetime(file, file_end='.png')
        time_list.append(time)
    time_list.sort() # put in chronological order
    time_list.append(time_list[-1]+timedelta(seconds=701)) # manually add last bin in case overlaps with next day

    return time_list


def time_bins(dir, freqs, day):
    time_list = start_times(dir, freqs, day)   

    bins = []
    
    for i in range(len(time_list)-1):
        bins.append((time_list[i], time_list[i+1]))

    return bins, time_list


def index_finder(file, freqs, bins, header):
    '''
    locate file's spot in array based on time and center frequency
    '''
    obs_time = get_datetime(file)
    center_frequency = header['frequency']/1e6

    t_i = 0 # initialize
    for i in range(len(bins)):
        if bins[i][0] <= obs_time < bins[i][1]:
            t_i = i
    
    f_i = np.where(freqs==center_frequency)[0]

    return t_i, f_i[0]


def passfail_plot(dir, freqs, day, show=False):
    '''
    D':
    '''
    # fill array with values corresponding to pass/fail checks
    # default all to pass and below go through the failed ones
    tbins, time_list = time_bins(dir, freqs, day) # for x-axis labelling
    test_array = passfail_array(freqs, tbins)

    # open CHECKME.txt file and get list of files with error
    check_file = os.path.join(dir, day+'.txt')
    sc16_list = []
    try:
        with open(check_file, 'r') as f:
            for line in f:
                sc16_list.append(line)
    except:
        print('No check file found in directory')

    if len(sc16_list)==0:
        print('No errors found on this day.')
        return

    # check 
    for file in sc16_list:
        sc16_file = remove_suffix(file, '\n')
        data, data_complex, file_beginning, header = get_data(sc16_file)

        # find where this file would be located in array
        t_i, f_i = index_finder(sc16_file, freqs, tbins, header)
                
        #############
        # bit check #
        #############
        if any(x in data for x in [1, 2, 3]):
            # add 1 in array
            test_array[t_i][f_i] += 1
        
        ####################################
        # integer count distribution check #
        ####################################
        if abs(data.mean()) > 1:
            # add 2 in array (so total is 3 if both fail)
            test_array[t_i][f_i] += 2

    ###### plot the errors ###########
    cmap = colors.ListedColormap(['white', 'salmon', 'royalblue', 'mediumpurple'])
    norm = colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)

    fig, ax = plt.subplots(1, 1, figsize=(24, 8))
    x_lims = [tbins[0][0], tbins[-1][1]]
    x_extent = mdates.date2num(x_lims) # basically defining axes
    y_extent = [freqs[0], freqs[-1]]
    
    im = ax.imshow(np.flip(test_array.T, 0), cmap=cmap, norm=norm, aspect='auto',
                    extent=(x_extent[0], x_extent[1], y_extent[0], y_extent[1]))
    ax.xaxis_date()
    date_format = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate() # set the x-axis data to diagonal so it fits better
    

    ax.set_xticks(time_list)
    plt.setp(ax.get_xticklabels()[1::2], visible=False) # show every other date label
    ax.set_yticks(freqs[::4]) # show every 4 frequencies so y-axis isn't crowded
    ax.yaxis.set_minor_locator(AutoMinorLocator(2)) # only showing some minor axes so eyes can follow easily

    ax.grid(axis='x', which='major', color='k', linestyle='-', linewidth=1)
    ax.grid(axis='y', which='minor', color='k', linestyle='-', linewidth=1)

    ax.set_title(time_list[0].strftime('%b %d %Y')) # set title as obs day
    ax.set_xlabel('Time of Observation')
    ax.set_ylabel('Central Frequency (MHz)')

    # create legend
    red_patch = mpatches.Patch(color='salmon', label='14->16 bit')
    blue_patch = mpatches.Patch(color='royalblue', label='|mean|>1')
    purple_patch = mpatches.Patch(color='mediumpurple', label='both')
    ax.legend(handles=[red_patch, blue_patch, purple_patch], loc='upper center', 
                        bbox_to_anchor=(0.5, -0.15), fancybox=True, ncol=3)

    plt.savefig(os.path.join(dir, day+'.png'), dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()

