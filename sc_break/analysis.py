from sc_break.parser import get_hs_data, set_shimnames, reset_shimnames, get_HCL_info, get_SCS_info, save_pulse_analysis_data, read_pulse_analysis_data
from sc_break.plotter import plot_hs_signal, subplot_hs_signal, sobplot_neighbors_hs_signal, plot_pulse_analysis, plot_all_signleSCS_pulse_analysis, plot_pulse_edge_analysis
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

    steps_to_skip = info.read().get('scb_analysis',{}).get('steps_to_skip', ['plot_hs_signal'])
    # filepath = os.path.abspath(filepath).replace('\\','/')

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
    splited = filepath.split(os.sep)
    if len(splited) > 2:
        splited.remove(splited[-2])
    filepath = os.sep.join(splited)

    SCS_savedir = os.path.join(os.path.dirname(filepath), f"SCS{SCSinfo['i']}")
    signal_all_savedir = os.path.join(SCS_savedir, 'signal_all')
    os.makedirs(signal_all_savedir, exist_ok=True)

    # signal_single_savedir = os.path.join(SCS_savedir, 'signal_single')
    # os.makedirs(signal_single_savedir, exist_ok=True)

    signal_neighbors_savedir = os.path.join(SCS_savedir, 'signal_neighbors')
    os.makedirs(signal_neighbors_savedir, exist_ok=True)

    pulse_analysis_savedir = os.path.join(SCS_savedir, 'pulse_analysis')
    os.makedirs(pulse_analysis_savedir, exist_ok=True)

    pulse_edges_savedir = os.path.join(pulse_analysis_savedir, 'edges')
    os.makedirs(pulse_edges_savedir, exist_ok=True)

    fname = os.path.basename(filepath).replace('.csv','')

    signal_filepath = os.path.join(signal_all_savedir, fname)
    signal_neighbors_filepath = os.path.join(signal_neighbors_savedir, fname)
    pulse_analysis_filepath = os.path.join(pulse_analysis_savedir, fname)
    pulse_edges_filepath = os.path.join(pulse_edges_savedir, fname)


    label = f'SCS: {metadata['scs']}\nHCL: {metadata['HCL']}'
    if "T" in metadata.keys():
        label += f'\nT={metadata['T']}'

    pulse_analysis = analyse_pulses(time, voltage)

    edge_analysis = analyse_pulse_edges(time, voltage, pulse_analysis['idle_mask'])

    # plot pulse edge analysis
    if 'plot_pulse_edge_analysis' not in steps_to_skip and edge_analysis is not None:
        plot_pulse_edge_analysis(edge_analysis, savepath=pulse_edges_filepath + f'_{flabel}_pulse_edge_analysis.{doc_format}')
    if 'plot_hs_signal' not in steps_to_skip:
        plot_hs_signal      (time, voltage, label, savepath=signal_filepath + f'_{flabel}_CSBAsignal.{doc_format}')
    # all signal plots
    if 'subplot_hs_signal' not in steps_to_skip:
        subplot_hs_signal   (time, voltage, label, savepath=signal_filepath + f'_{flabel}_CSBAsignal_subplots.{doc_format}')
    if 'sobplot_neighbors_hs_signal' not in steps_to_skip:
        sobplot_neighbors_hs_signal (time, voltage, label, savepath=signal_neighbors_filepath + f'_{flabel}_CSBAsignal_neighbots.{doc_format}')

    if 'save_pulse_analysis_data' not in steps_to_skip:
        save_pulse_analysis_data(pulse_analysis, pulse_analysis_filepath + f'_{flabel}_pulse_analysis.csv')
    if 'plot_pulse_analysis' not in steps_to_skip:
        plot_pulse_analysis(pulse_analysis, signal, label, savepath=pulse_analysis_filepath + f'_{flabel}_pulse_analysis.{doc_format}')

    # plot_pulses(pulse_analysis, label, savepath=os.path.join(pulse_analysis_savedir, fname + f'_{flabel}_pulse_analysis.{doc_format}'))
    
def analyse_scba_indir(dirpath, out_doc_format='png'):
    index_range_to_analyse = info.read().get('scb_analysis',{}).get('index_range_to_analyse', [None, None])

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
        for file in files[index_range_to_analyse[0]:index_range_to_analyse[1]]:
            # make a plot
            analyse_scba(file, doc_format= out_doc_format)

            try:
                plt.close('all')  # close all open figures
            except Exception:
                pass
            gc.collect()
            
    plot_all_pulse_analyses(dirpath=dirpath, out_doc_format= out_doc_format)

def analyse_pulses(
        time, 
        voltage, 
        margin_frac = {'idle': 0.05, 'pulse': 0.05}, 
        margin_abs= {'idle': 200, 'pulse': -100}, 
        threshold_std = 2.,
        threshold_abs=0.01,
    ):
    metadata = METADATA[0]
    HCLinfo = get_HCL_info(metadata)
    SCSinfo = get_SCS_info(metadata)
    # exit()
    ignore_before_t0 = info.read().get('scb_analysis',{}).get('ignore_before_t0', False)
    margin_frac = info.read().get('scb_analysis',{}).get('pulse_crop_margin_frac', margin_frac)
    margin_abs = info.read().get('scb_analysis',{}).get('pulse_crop_margin_abs', margin_abs)
    threshold_std = info.read().get('scb_analysis',{}).get('pulse_threshold_std', threshold_std)
    threshold_abs = info.read().get('scb_analysis',{}).get('pulse_threshold_abs', threshold_abs)
    t_u = HCLinfo['u']*1e3
    t_d = HCLinfo['d']*1e3
    warmup_time = SCSinfo.get('h', 0)*1e3
    cooldown_time = SCSinfo.get('c', 0)*1e3

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
    # margin_frac = 0.3  # 
    margin_idle = min(t_d * margin_frac['idle'], t_d / 2.0, margin_abs['idle'])
    margin_pulse = min(t_u * margin_frac['pulse'], t_u / 2.0, margin_abs['pulse'])

    # time_shift_per_channel = info.read().get('scb_analysis',{}).get('time_shift_per_channel', [])

    # Determine cycle index for each sample
    cycles = np.floor(time / period).astype(int)
    unique_cycles = np.unique(cycles)

    n_ch = voltage.shape[1]
    centers = []
    idle_means_list = []
    pulse_means_list = []
    pulse_values_list = []

    # Global masks aligned to original time array
    idle_mask = np.zeros(time.shape[0], dtype=bool)
    pulse_mask = np.zeros(time.shape[0], dtype=bool)
    
    # loop over cycles
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
        pulse_n_mask0 = pulse_n_mask.copy()
        pulse_n_mask_ch = np.tile(pulse_n_mask[:, np.newaxis], (1, n_ch))


        if not idle_n_mask.any() or not pulse_n_mask.any() or (ignore_before_t0 and np.all(t_n < 0)) or np.any(t_n > (warmup_time + cooldown_time)):
            continue
        
        idle_v_n = v_n[idle_n_mask, :]
        pulse_v_n = v_n[pulse_n_mask, :]


        pulse_values = np.zeros((n_ch,), dtype=np.float64)
        # 2nd order polynomial fit of pedestal to idle region
        for ch in range(n_ch):
            idle_times_ch = t_n[idle_n_mask]
            idle_voltages_ch = idle_v_n[:, ch]
            v_n_ch = v_n[:, ch]

            pulse_times_ch = t_n[pulse_n_mask]
            pulse_voltages_ch = pulse_v_n[:, ch]

            if len(idle_times_ch) < 3:
                continue  # Not enough points to fit

            # Fit 2nd order polynomial
            coeffs = np.polyfit(idle_times_ch, idle_voltages_ch, 2)
            poly_fit = np.poly1d(coeffs)
            fit_values = poly_fit(t_n)


            # get std of residuals
            residuals = v_n[:,ch] - fit_values
            std_residuals = np.std(residuals)

            threshold = fit_values + threshold_std*std_residuals


            # apply threshold to pulse region
            # if threshold_abs is not None:
            pulse_n_mask_ch[:,ch] &= (v_n[:,ch] > threshold)# & (pulse_voltages_ch > threshold_abs)


            if all(~pulse_n_mask_ch[:,ch]):
                # if all pulse points are filtered out, use original 
                pulse_n_mask = pulse_n_mask0.copy()
                pulse_n_mask_ch[:,ch] = pulse_n_mask0.copy()

            # subtract pedestal from pulse values
            pulse_values[ch] = np.mean(v_n[:,ch][pulse_n_mask_ch[:,ch]] - fit_values[pulse_n_mask_ch[:,ch]])
                # continue

            # pulse_n_mask &= (pulse_voltages_ch > threshold)

            # Subtract fitted pedestal from both idle and pulse regions
            # idle_v_n_fit = poly_fit(idle_times_ch)
            # v_n[pulse_n_mask, ch] -= poly_fit(t_n[pulse_n_mask])

        #     pulse plotting for debug
        #     if ch == 0: plt.title(f'Cycle {n}')
        #     plt.subplot(n_ch,1,ch+1)
        #     plt.plot(idle_times_ch, idle_voltages_ch, 'o', label='Idle Data')
        #     plt.plot(t_n, fit_values, '-', label='fit')
        #     plt.plot(idle_times_ch, poly_fit(idle_times_ch) + threshold_std*std_residuals, '-', label='upper')
        #     plt.plot(t_n[pulse_n_mask0], v_n_ch[pulse_n_mask0], 'x', label='pulse Data')
        #     plt.plot(t_n[pulse_n_mask_ch[:,ch]], v_n[:,ch][pulse_n_mask_ch[:,ch]], 'g.', label='pulse Data over threshold')
        #     plt.plot(t_n, threshold, label='pulse Data')

        # plt.show()

        # if not np.any(pulse_n_mask):
        #     continue

        # Update global masks
        idle_mask[cyc_idx[idle_n_mask]] = True
        pulse_mask[cyc_idx[pulse_n_mask]] = True

        idle_mean = np.nanmean(v_n[idle_n_mask, :], axis=0)
        pulse_mean = np.nanmean(v_n[pulse_n_mask_ch], axis=0)

        idle_means_list.append(idle_mean)
        pulse_means_list.append(pulse_mean)
        pulse_values_list.append(pulse_values)

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
        pulse_height = np.vstack(pulse_values_list) 

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
        "idle_mask": idle_mask,
        "channels": [[],[]]
    }

def analyse_pulse_edges(time, voltage, idle_mask):
    metadata = METADATA[0]

    # transpose voltage if needed
    voltage = np.asarray(voltage)
    if voltage.shape[0] != time.shape[0]:
        if voltage.shape[1] == time.shape[0]:
            voltage = voltage.T
        else:
            raise ValueError("voltage's time dimension must match the length of time (either axis 0 or 1)")
    HCLinfo = get_HCL_info(metadata)
    t_u = HCLinfo['u']*1e3
    t_d = HCLinfo['d']*1e3
    period = t_u + t_d
    pulse_region_mask = ~idle_mask

    # Identify pulse regions (where idle_mask is False)
    pulse_indices = np.where(pulse_region_mask)[0]

    if len(pulse_indices) == 0:
        return None

    # Find discontinuities in pulse indices (gaps indicate separate pulses)
    gaps = np.diff(pulse_indices) > 1
    gap_positions = np.where(gaps)[0]

    # Split indices at gaps
    if len(gap_positions) == 0:
        pulse_chunks_idx = [pulse_indices]
    else:
        split_positions = gap_positions + 1
        pulse_chunks_idx = np.split(pulse_indices, split_positions)

    # Create time and voltage chunks
    time_chunks = []
    voltage_chunks = []
    for chunk_idx in pulse_chunks_idx:
        time_chunks.append(((time[chunk_idx] - period/2) % period) + period/2)
        voltage_chunks.append(voltage[chunk_idx, :])

    # testplot 
    # plt.figure()
    # for time_chunk, voltage_chunk in zip(time_chunks, voltage_chunks):
    #     for ch in range(voltage_chunk.shape[1]):
    #         plt.plot(time_chunk, voltage_chunk[:, ch],  label=f'Ch {ch+1}', )
    #     plt.xlabel('Time (ms)')
    #     plt.ylabel('Voltage (V)')
    #     plt.title('Pulse Segment')
    # plt.show()
    # exit()
    pulse_edge_analysis = {
        "time_chunks": time_chunks,
        "voltage_chunks": voltage_chunks,
    }

    return pulse_edge_analysis
    # 


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
    vpp0, vpp1 = None, None
    vpp_range = info.read().get('scb_analysis',{}).get('all_pulse_analysis_plot',{}).get('vpp_range', None)
    index_range_to_analyse = info.read().get('scb_analysis',{}).get('index_range_to_analyse', [None, None])
    
    splited = dirpath.split(os.sep)
    if len(splited) > 2:
        splited.remove(splited[-2])
    dirpath = os.sep.join(splited)

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
        files = [f for f in files if f.endswith('.csv')][index_range_to_analyse[0]:index_range_to_analyse[1]]
        
        i_SCS = int(scs_dir.split('SCS')[-1])


        print(f"Plotting all pulse analyses for SCS {i_SCS} from directory: {pulse_analysis_dir}")
        pulse_analysis_data = []
        # read files 
        for file in files[index_range_to_analyse[0]:index_range_to_analyse[1]]:
            filepath = os.path.join(pulse_analysis_dir, file)
            pulse_analysis_data.append(read_pulse_analysis_data(filepath))
        
        # sort data by Vpp
        pulse_analysis_data.sort(key=lambda x: x['Vpp'])

        # print("pulse_analysis_data")
        # print(pulse_analysis_data[0:2])
        # exit()

        

        # average signals with same Vpp
        averaged_data = []
        current_Vpp = None
        current_group = []
        for data in pulse_analysis_data:
            if data['Vpp'] != current_Vpp:
                if current_group:
                    try:
                        # average current group
                        
                        avg_data = {
                        'Vpp': current_Vpp,
                        'time': current_group[0]['time'],
                        'pulses': np.nanmean([d['pulses'] for d in current_group], axis=0),
                        'error': np.nanstd([d['pulses'] for d in current_group], axis=0),
                        }
                        averaged_data.append(avg_data)
                    except Exception as e:
                        print(f"Error averaging data for Vpp={current_Vpp}: {e}")
                        # print array sizes
                        for d in current_group:
                            print(f"Data shape in file {d['filepath']}: {d['pulses'].shape}")
                        print("Skipping this group.")

                        
                current_Vpp = data['Vpp']
                current_group = [data]
            else:
                current_group.append(data)

        # handle last group
        if current_group:
            avg_data = {
            'Vpp': current_Vpp,
            'time': current_group[0]['time'],
            'pulses': np.nanmean([d['pulses'] for d in current_group], axis=0),
            'error': np.nanstd([d['pulses'] for d in current_group], axis=0),
            }
            averaged_data.append(avg_data)
        pulse_analysis_data = averaged_data

        # get vpp range for filename
        if vpp_range is not None:
            vpp0, vpp1 = vpp_range
        else:
            vpp0, vpp1 = pulse_analysis_data[0]['Vpp'], pulse_analysis_data[-1]['Vpp']

        plot_all_signleSCS_pulse_analysis(pulse_analysis_data, i_scs=int(i_SCS), label=f'SCS={i_SCS}', savedir=pulse_analysis_dir)

