from sc_break.parser import get_hs_data, set_shimnames, reset_shimnames, get_HCL_info, get_SCS_info, save_pulse_analysis_data, read_pulse_analysis_data
from sc_break.plotter import plot_hs_signal, subplot_hs_signal, sobplot_neighbors_hs_signal, plot_pulse_analysis, plot_signleSCS_pulse_analysis
from sc_break import  SHIM_ORDER, SHIM_CHANNELS, SHIM13_ORDER, METADATA
from matplotlib import pyplot as plt

import os, gc
import numpy as np
import gc_utils.info as info
# np.seterr(invalid='ignore')
DOC_FORMATS = ['png','pdf']
# print(SHIM_CHANNELS)
def analyse_scba(filepath, label=None, doc_format='png'):
    # load info cfg
    # plot_info = info.read().get('plot',{})


    reset_shimnames()
    # check if doc_format is valid
    if doc_format not in DOC_FORMATS:
        doc_format = DOC_FORMATS[0]
    # get filename
    print("Plotting HS data of SC break attempt from file:", filepath)
    time, voltage, metadata = get_hs_data(filepath)
    # filter outliers in voltage data
    voltage = filter_outliers(voltage)

    signal = time.copy(), voltage.copy()
    set_shimnames(metadata) # based on channels configuration
    
    SCSinfo = get_SCS_info(metadata)
    flabel = f'SCS={SCSinfo['i']}_VPP={SCSinfo['Vpp']}'

    # make directory for specific SCS and it's plot categories
    SCS_savedir = os.path.join(os.path.dirname(filepath), f"SCS{SCSinfo['i']}")
    signal_all_savedir = os.path.join(SCS_savedir, 'signal_all')
    os.makedirs(signal_all_savedir, exist_ok=True)

    # signal_single_savedir = os.path.join(SCS_savedir, 'signal_single')
    # os.makedirs(signal_single_savedir, exist_ok=True)

    signal_neighbors_savedir = os.path.join(SCS_savedir, 'signal_neighbors')
    os.makedirs(signal_neighbors_savedir, exist_ok=True)

    pulse_analysis_savedir = os.path.join(SCS_savedir, 'pulse_analysis')
    os.makedirs(pulse_analysis_savedir, exist_ok=True)

    fname = os.path.basename(filepath).replace('.csv','')

    signal_filepath = os.path.join(signal_all_savedir, fname)
    signal_neighbors_filepath = os.path.join(signal_neighbors_savedir, fname)
    pulse_analysis_filepath = os.path.join(pulse_analysis_savedir, fname)


    label = f'SCS: {metadata['scs']}\nHCL: {metadata['HCL']}'
    if "T" in metadata.keys():
        label += f'\nT={metadata['T']}'
    
    # all signal plots
    # plot_hs_signal      (time, voltage, label, savepath=signal_filepath + f'_{flabel}_CSBAsignal.{doc_format}')
    subplot_hs_signal   (time, voltage, label, savepath=signal_filepath + f'_{flabel}_CSBAsignal_subplots.{doc_format}')
    sobplot_neighbors_hs_signal (time, voltage, label, savepath=signal_neighbors_filepath + f'_{flabel}_CSBAsignal_neighbots.{doc_format}')

    pulse_analysis = sep_idle_pulse_signal(time, voltage)
    save_pulse_analysis_data(pulse_analysis, pulse_analysis_filepath + f'_{flabel}_pulse_analysis.csv')
    plot_pulse_analysis(pulse_analysis, signal, label, savepath=pulse_analysis_filepath + f'_{flabel}_pulse_analysis.{doc_format}')

    # plot_pulses(pulse_analysis, label, savepath=os.path.join(pulse_analysis_savedir, fname + f'_{flabel}_pulse_analysis.{doc_format}'))
    
def analyse_scba_indir(dirpath, out_doc_format='png'):
    # get files in directory
    files = os.listdir(dirpath)
    # filter .csv
    files = [f for f in files if f.startswith('HS_reading_') and f.endswith('.csv')]
    # get full paths
    files = [dirpath + f for f in files]
    
    # # exit()
    if info.read().get('scb_analysis',{}).get('analyse_SCBAs',True) is not True:
        print("SCB analysis disabled in info.toml. Skipping SCB analysis.")
    else: 
        for file in files:
            # make a plot
            analyse_scba(file, doc_format= out_doc_format)

            try:
                import matplotlib.pyplot as plt
                plt.close('all')  # close all open figures
            except Exception:
                pass
            gc.collect()
    plot_all_pulse_analyses(dirpath=dirpath, out_doc_format= out_doc_format)

def sep_idle_pulse_signal(time, voltage, margin_frac = 0.3):
    metadata = METADATA[0]
    HCLinfo = get_HCL_info(metadata)

    t_u = HCLinfo['u']*1e3
    t_d = HCLinfo['d']*1e3
    # Separate samples by periodic idle (t_d) and pulse (t_u) phases.
    time = np.asarray(time)
    voltage = np.asarray(voltage)

    if time.ndim != 1:
        raise ValueError("time must be 1D")
    if voltage.ndim != 2:
        raise ValueError("voltage must be 2D")

    # Adjust orientation so that the first dimension of voltage matches time
    if voltage.shape[0] != time.shape[0]:
        if voltage.shape[1] == time.shape[0]:
            voltage = voltage.T
        else:
            raise ValueError("voltage's time dimension must match the length of time (either axis 0 or 1)")
    period = t_u + t_d
    if period <= 0:
        raise ValueError("Invalid HCL durations: t_u + t_d must be > 0")

    # First segment is idle (t_d), then pulse (t_u), repeating
    phase = np.mod(time, period)
    
    # Add small margins around boundaries to avoid edge effects
    margin_frac = 0.3  # 5% margin
    margin_idle = min(t_d * margin_frac, t_d / 2.0)
    margin_pulse = min(t_u * margin_frac, t_u / 2.0)

    # Determine cycle index for each sample
    cycles = np.floor(time / period).astype(int)
    unique_cycles = np.unique(cycles)

    n_ch = voltage.shape[1]
    centers = []
    idle_means_list = []
    pulse_means_list = []

    # Global masks aligned to original time array
    idle_mask = np.zeros(time.shape[0], dtype=bool)
    pulse_mask = np.zeros(time.shape[0], dtype=bool)
    for n in unique_cycles:
        cyc_mask = cycles == n
        if not np.any(cyc_mask):
            continue

        cyc_idx = np.where(cyc_mask)[0]
        phase_n = phase[cyc_idx]
        t_n = time[cyc_idx]
        v_n = voltage[cyc_idx, :]

        # Masks within this cycle
        idle_n_mask = (phase_n >= margin_idle) & (phase_n < t_d - margin_idle)
        pulse_n_mask = (phase_n >= t_d + margin_pulse) & (phase_n < period - margin_pulse)

        if not idle_n_mask.any() or not pulse_n_mask.any() or np.all(t_n < 0):
            continue
        
        # Update global masks
        idle_mask[cyc_idx[idle_n_mask]] = True
        pulse_mask[cyc_idx[pulse_n_mask]] = True

        idle_mean = np.nanmean(v_n[idle_n_mask, :], axis=0)
        pulse_mean = np.nanmean(v_n[pulse_n_mask, :], axis=0)

        idle_means_list.append(idle_mean)
        pulse_means_list.append(pulse_mean)

        # Assign time as the center of the pulse window (use mean pulse sample time)
        centers.append(t_n[pulse_n_mask].mean())
    if len(centers) == 0:
        pulse_time = np.array([])
        pulse_avg = np.empty((0, n_ch))
        idle_avg = np.empty((0, n_ch))
        pulse_height = np.empty((0, n_ch))
    else:
        pulse_time = np.array(centers)
        pulse_avg = np.vstack(pulse_means_list)
        idle_avg = np.vstack(idle_means_list)
        pulse_height = pulse_avg - idle_avg

    # Optional quick look plot (disabled by default)
    # plt.figure()
    # if pulse_time.size > 0 and pulse_height.shape[1] > 12:
    #     plt.plot(time[pulse_mask]/1000.0, voltage[pulse_mask,4], "-o")
    #     plt.plot(time[idle_mask]/1000.0, voltage[idle_mask,4], "-")
    #     plt.xlabel("Time (s)")
    #     plt.ylabel("Pulse height (V)")
    # plt.show()

    return {
        "pulse_time": pulse_time,
        "pulse_height": pulse_height,
        "pulse_avg": pulse_avg,
        "idle_avg": idle_avg,
        "pulse_mask": pulse_mask,
        "idle_mask": idle_mask
    }

def filter_outliers(data, threshold=None):
    """
    Remove outliers from data using Z-score method.
    Parameters:
        - data: array-like, input data
        - m: float, threshold multiplier for standard deviation
    Returns:
        - filtered_data: array-like, data with outliers removed
    """
    if threshold is None:
        # load from info.toml
        plot_info = info.read().get('scb_analysis',{})
        threshold = plot_info.get('filter_threshold_mV', 0)  # default 0 mV - no filetring
    if threshold <= 1e-9:
        return data  # no filtering needed:

    filtered_data = np.copy(data)
    for i in range(filtered_data.shape[1]):
        mask = np.abs(filtered_data[:, i]) > threshold
        filtered_data[mask, i] = np.nan
    
    return filtered_data
    

def plot_all_pulse_analyses(dirpath, out_doc_format='png'):
    
    # get SCS directories
    scs_dirs = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, d)) and d.startswith('SCS')]
    for scs_dir in scs_dirs:
        # get pulse analysis directory
        pulse_analysis_dir = os.path.join(scs_dir, 'pulse_analysis')
        if not os.path.isdir(pulse_analysis_dir):
            continue
        # get files in directory
        files = os.listdir(pulse_analysis_dir)
        # filter .csv
        files = [f for f in files if f.endswith('.csv')]
        
        i_SCS = int(scs_dir.split('SCS')[-1])


        print(f"Plotting all pulse analyses for SCS {i_SCS} from directory: {pulse_analysis_dir}")
        pulse_analysis_data = []
        # read files 
        for file in files:
            filepath = os.path.join(pulse_analysis_dir, file)
            pulse_analysis_data.append(read_pulse_analysis_data(filepath))
        
        # sort data by Vpp
        pulse_analysis_data.sort(key=lambda x: x['Vpp'])
        plot_signleSCS_pulse_analysis(pulse_analysis_data, channel_idx=int(i_SCS-1), label=f'SCS={i_SCS}', savepath=os.path.join(pulse_analysis_dir, f'SCS{i_SCS}_all_pulse_analysis.{out_doc_format}'))

