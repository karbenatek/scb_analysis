from sc_break.parser import get_hs_data, set_shimnames, reset_shimnames, get_HCL_info, get_SCS_info, save_pulse_analysis_data, read_pulse_analysis_data, parse_SCS_profiles_from_stage
from sc_break.plotter import plot_pulse_height_histogram, plot_averaged_rep_stage_pulses, plot_flux_decay, plot_pumping_vs_hcl_current, plot_SCS_profile_pulse_analysis, plot_SCS_profile_sliced, plot_SCS_profile_with_repetitions, plot_SCS_profiles, plot_flux_pumping, plot_hs_signal, plot_pulse_sanity, subplot_hs_signal, sobplot_neighbors_hs_signal, plot_pulse_analysis, plot_all_signleSCS_pulse_analysis, plot_pulse_edge_analysis
from sc_break import *
# from sc_break import  SHIM_ORDER, SHIM_CHANNELS, SHIM13_ORDER, METADATA
from matplotlib import pyplot as plt
from sc_break.routine_fun import find_HS_reading_indir, get_HS_reading_indir, split_arrays_by_period
import os, gc
import numpy as np
import gc_utils.info as info
# np.seterr(invalid='ignore')
# DOC_FORMATS = ['png','pdf']
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
    
    flabel = f'SCS={SCSinfo["i"]}_VPP={SCSinfo["Vpp"]}' if SCSinfo is not None else 'SCS_unknown'

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


    label = f"SCS: {metadata.get('scs', 'N/A')}\nHCL: {metadata.get('HCL', 'N/A')}"
    if 'T' in metadata:
        label += f"\nT={metadata['T']}"

    pulse_analysis = analyse_scb_pulses(time, voltage, pedestal_fit_order=0)
    edge_analysis = analyse_pulse_edges(time, voltage, pulse_analysis)

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
    files = find_HS_reading_indir(dirpath)
    

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

def analyse_stages_pulses(SCS_stage):
    # placeholder for pulse analysis function
    # for now just return time and voltage as is
    return

def analyse_pulses(
        time,
        voltage,
        t_u,
        t_d,
        warmup_time=0,
        cooldown_time=0,
        ignore_before_t0=False,
        margin_frac=None,
        margin_abs=None,
        threshold_n_stds=2.,
        threshold_abs=0.01,
        pedestal_fit_order=2,
    ):

    if margin_frac is None:
        margin_frac = {'idle': 0.05, 'pulse': 0.05}
    if margin_abs is None:
        margin_abs = {'idle': 200, 'pulse': 100}

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
    margin_idle = min(t_d * margin_frac['idle'], t_d / 2.0, margin_abs['idle'])
    margin_pulse = min(t_u * margin_frac['pulse'], t_u / 2.0, margin_abs['pulse'])

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
    pedfit_values = np.zeros_like(voltage, dtype=np.float64)

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
        pulse_n_mask_ch = np.tile(pulse_n_mask[:, np.newaxis], (1, n_ch))

        if not idle_n_mask.any() or not pulse_n_mask.any() or (ignore_before_t0 and np.all(t_n < 0)) or (np.any(t_n > (warmup_time + cooldown_time)) and (warmup_time + cooldown_time) > 0):
            continue

        idle_v_n = v_n[idle_n_mask, :]
        pulse_v_n = v_n[pulse_n_mask, :]

        pulse_values = np.zeros((n_ch,), dtype=np.float64)
        fit_n_values = np.zeros((n_ch, len(t_n)), dtype=np.float64)
        # polynomial fit of pedestal to idle region
        for ch in range(n_ch):
            idle_times_ch = t_n[idle_n_mask]
            idle_voltages_ch = idle_v_n[:, ch]

            if len(idle_times_ch) < 3:
                continue  # Not enough points to fit

            # Fit polynomial pedestal
            coeffs = np.polyfit(idle_times_ch, idle_voltages_ch, pedestal_fit_order)
            poly_fit = np.poly1d(coeffs)
            fit_values = poly_fit(t_n)
            fit_n_values[ch] = fit_values

            # get std of residuals
            residuals = v_n[:, ch] - fit_values
            std_residuals = np.std(residuals)

            # apply threshold to pulse region
            if threshold_n_stds > 1e-9:
                threshold = threshold_n_stds * std_residuals
                pulse_n_mask_ch[:, ch] &= (np.abs(v_n[:, ch]) >= threshold)
            if threshold_abs > 0:
                pulse_n_mask_ch[:, ch] &= (np.abs(v_n[:, ch]) >= threshold_abs)

            pulse_values[ch] = np.mean(v_n[:, ch][pulse_n_mask_ch[:, ch]] - fit_values[pulse_n_mask_ch[:, ch]])

        # Update global masks
        idle_mask[cyc_idx[idle_n_mask]] = True
        pulse_mask[cyc_idx[pulse_n_mask]] = True
        pedfit_values[cyc_idx, :] = fit_n_values.T

        idle_mean = np.nanmean(v_n[idle_n_mask, :], axis=0)
        pulse_mean = np.nanmean(v_n[pulse_n_mask_ch], axis=0)

        idle_means_list.append(idle_mean)
        pulse_means_list.append(pulse_mean)
        pulse_values_list.append(pulse_values)
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

    return {
        "pulse_time": pulse_time,
        "pulse_height": pulse_height,
        "pulse_avg": pulse_avg,
        "idle_avg": idle_avg,
        "pulse_mask": pulse_mask,
        "idle_mask": idle_mask,
        "pedestal_fit": pedfit_values,
        "pulse_interval": (t_d + margin_pulse, period - margin_pulse),
        "idle_interval": (margin_idle, t_d - margin_idle),
    }


def analyse_scb_pulses(
        time,
        voltage,
        margin_frac = {'idle': 0.05, 'pulse': 0.05},
        margin_abs= {'idle': 200, 'pulse': 100},
        threshold_n_stds = 2.,
        threshold_abs=0.01,
        pedestal_fit_order=2,
    ):

    metadata = METADATA[0]
    HCLinfo = get_HCL_info(metadata)
    if HCLinfo is None:
        print("No HCL info found in metadata. Cannot analyse pulses without HCL timing information.")
        return None
    SCSinfo = get_SCS_info(metadata)
    ignore_before_t0 = info.read().get('scb_analysis',{}).get('ignore_before_t0', False)
    margin_frac = info.read().get('scb_analysis',{}).get('pulse_crop_margin_frac', margin_frac)
    margin_abs = info.read().get('scb_analysis',{}).get('pulse_crop_margin_abs', margin_abs)
    threshold_n_stds = info.read().get('scb_analysis',{}).get('pulse_threshold_n_stds', threshold_n_stds)
    threshold_abs = info.read().get('scb_analysis',{}).get('pulse_threshold_abs', threshold_abs)
    t_u = HCLinfo['u']*1e3
    t_d = HCLinfo['d']*1e3
    warmup_time = SCSinfo.get('h', 0)*1e3
    cooldown_time = SCSinfo.get('c', 0)*1e3

    return analyse_pulses(
        time=time,
        voltage=voltage,
        t_u=t_u,
        t_d=t_d,
        warmup_time=warmup_time,
        cooldown_time=cooldown_time,
        ignore_before_t0=ignore_before_t0,
        margin_frac=margin_frac,
        margin_abs=margin_abs,
        threshold_n_stds=threshold_n_stds,
        threshold_abs=threshold_abs,
        pedestal_fit_order=pedestal_fit_order,
    )

def analyse_pulse_edges(time, voltage, pulse_analysis):
    metadata = METADATA[0]
    idle_mask = pulse_analysis['idle_mask']
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

def analyse_scs_profile(filepath, doc_format='png'):
    # load info cfg
    # plot_info = info.read().get('plot',{})
    """TODO: 
    - identify 
    """
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
    
    # make directory for specific SCS and it's plot categories

    savedir = os.path.dirname(filepath)

    fname = filepath.replace('.csv','')



    if 'T' in metadata:
        label += f"\nT={metadata['T']}"

    pulse_analysis = analyse_scb_pulses(time, voltage, pedestal_fit_order=0)
    pulse_sanity_analysis = analyse_pulse_sanity(time, voltage, pulse_analysis)
    
    SCS_profiles = metadata.get('SCS_profiles', {})

    # plotting and saving results
    if 'plot_SCS_profile_with_repetitions' not in steps_to_skip:
        plot_SCS_profile_with_repetitions(time, voltage, SCS_profiles, pulse_analysis, savepath=fname + f'_SCS_w_reps.{doc_format}')
    if 'subplot_hs_signal' not in steps_to_skip:
        subplot_hs_signal   (time, voltage, savepath=fname + f'_HSsignal_subplots.{doc_format}')
    if 'pulse_sanity' not in steps_to_skip:
        # plot_pulse_sanity(time, voltage, pulse_analysis, pulse_sanity_analysis)
        plot_pulse_sanity(time, voltage, pulse_analysis, pulse_sanity_analysis, fname + f'_pulse_sanity.{doc_format}')
    
        
    if 'all_edge_intervals' not in steps_to_skip:
        plot_SCS_profile_sliced(time, voltage, SCS_profiles, slice_type='all_edges', savepath=fname + f'_all_edge_intervals.{doc_format}')
    else:
        if 'rising_edge_intervals' not in steps_to_skip:
            plot_SCS_profile_sliced(time, voltage, SCS_profiles, slice_type='rising_edge', savepath=fname + f'_rising_edge_intervals.{doc_format}')
        if 'falling_edge_intervals' not in steps_to_skip:
            plot_SCS_profile_sliced(time, voltage, SCS_profiles, slice_type='falling_edge', savepath=fname + f'_falling_edge_intervals.{doc_format}')
    
    
    if 'save_pulse_analysis_data' not in steps_to_skip:
        save_pulse_analysis_data(pulse_analysis, fname + f'_pulse_analysis.csv')
    


    return
    
    if 'scs_profiles' not in steps_to_skip:
        if SCS_profiles:
            plot_SCS_profiles(SCS_profiles, savepath=fname + f'_SCS_profiles.{doc_format}')
    # than plot raw signal
    # if 'plot_pulse_analysis' not in steps_to_skip:
    #     plot_pulse_analysis(pulse_analysis, signal, savepath=fname + f'_pulse_analysis.{doc_format}')
    if 'plot_pulse_analysis' not in steps_to_skip:
        plot_pulse_analysis(pulse_analysis, signal, savepath=fname + f'_pulse_analysis.{doc_format}')

def find_and_analyse_scs_profiles(dirpath, doc_format='png'):
    # get all files in directory and subdirectories
    files = find_HS_reading_indir(dirpath)
    errors = []
    for file in files:
        try:
            print(f"Analyzing file: {file}")
            analyse_scs_profile(file, doc_format=doc_format)
        except Exception as e:
            errors.append((file, e))
    
    if errors:
        print("Errors occurred in the following files:")
        for file, error in errors:
            print(f"{file}: {error}")
        

def analyse_pulse_sanity(time, voltage, pulse_analysis):
    
    # transpose voltage if needed
    voltage = np.asarray(voltage)
    if voltage.shape[0] != time.shape[0]:
        if voltage.shape[1] == time.shape[0]:
            voltage = voltage.T
        else:
            raise ValueError("voltage's time dimension must match the length of time (either axis 0 or 1)")
    
    # get pulse timing
    metadata = METADATA[0]
    HCLinfo = get_HCL_info(metadata)
    if HCLinfo is None:
        print("No HCL info found in metadata. Cannot analyse pulses without HCL timing information.")
        return None
    t_u = HCLinfo['u']*1e3
    t_d = HCLinfo['d']*1e3
    period = t_u + t_d

    
    # get time referenced to pulse period
    referenced_time = np.mod(time, period)

    # split time, voltage and masks into pulse segment chunks
    time_chunks = []
    voltage_chunks = []
    idle_mask_chunks = []
    pulse_mask_chunks = []
    pedestal_fit_chunks = []
    i_0 = 0
    for i,t in enumerate(referenced_time):
        if i == 0:
            continue
        if referenced_time[i-1] > referenced_time[i]:
            time_chunks.append(referenced_time[i_0:i-1])
            voltage_chunks.append(voltage[i_0:i-1, :])
            idle_mask_chunks.append(pulse_analysis['idle_mask'][i_0:i-1])
            pulse_mask_chunks.append(pulse_analysis['pulse_mask'][i_0:i-1])
            pedestal_fit_chunks.append(pulse_analysis['pedestal_fit'][i_0:i-1, :])
            i_0 = i

    return { 
        "time_chunks": time_chunks,
        "voltage_chunks": voltage_chunks,
        "idle_mask_chunks": idle_mask_chunks,
        "pulse_mask_chunks": pulse_mask_chunks,
        "pedestal_fit_chunks": pedestal_fit_chunks,

    }

def add_signal_to_SCS_stages(SCS_stages, t, v):
    t_shift = 0
    _t = t.copy()
    _v = v.copy()
    for i_stage, stage in enumerate(SCS_stages):
        if stage['Name'] == 'analysis':
            continue
        stage['t_shift'] = t_shift
        
        profile_length = 0.
        # find longest profile in stage = profile length
        for profile in stage['SCS profiles']:
            for op in profile['SCS op']:
                profile_length = max(profile_length, op['Time (s)'])

        stage_length = stage['# rep'] * profile_length

        stage['stage_length'] = stage_length
        stage['profile_length'] = profile_length

        t_stage = _t[_t <= stage_length*1000]
        stage['t'] = t_stage.copy()
        t_orig = t_stage + t_shift*1000
        stage['t_orig'] = t_orig.copy()
        _t = _t[_t > stage_length*1000] - stage_length*1000
        v_stage = _v[:len(t_stage),:]
        stage['v'] = v_stage.copy()
        _v = _v[len(t_stage):,:]
        t_shift += stage_length

def analyse_flux_pumping(SCS_stages):
    s1_recovery = info.read().get('stages',{}).get('shim1_recovery_time',15)
    s2_recovery = info.read().get('stages',{}).get('shim2_recovery_time',15)
    SCS_stages.append({'Name': 'analysis'})


    # variables for values after fluxshing or alignment
    t_0 = None
    v_0 = None
    vrms_0 = None
    for i_stage, stage in enumerate(SCS_stages):
        if stage['Name'] == 'analysis':
            continue
        t_stage = stage['t']
        v_stage = stage['v']
        t_shift = stage['t_shift']
        profile_length = stage['profile_length']
        if stage['Name'] == 'flux_alignment':
            for profile in stage['SCS profiles']:
                if profile['SCS no.'] == 1:
                    for op in profile['SCS op']:
                        if op['Duty-cycle (%)'] == 0:
                            t_aligned = op['Time (s)']
                            break 
                    
            mask_aligned = t_stage >= t_aligned*1000
            
            t_aligned = t_stage[mask_aligned].mean()
            stage['t_aligned'] = t_aligned

            v_aligned = v_stage[mask_aligned].mean(axis=0)
            stage['v_aligned'] = v_aligned

            vrms_aligned = v_stage[mask_aligned].std(axis=0)
            
            stage['vrms_aligned'] = vrms_aligned
            
            t_aligned += t_shift # go to global time
            t_0 = t_aligned
            v_0 = v_aligned
            vrms_0 = vrms_aligned

            if 't_aligned' not in SCS_stages[-1].keys():
                SCS_stages[-1]['t_aligned'] = np.array([t_aligned])
                SCS_stages[-1]['v_aligned'] = np.array([v_aligned])
                SCS_stages[-1]['vrms_aligned'] = np.array([vrms_aligned])
            else:
                SCS_stages[-1]['t_aligned'] = np.append(SCS_stages[-1]['t_aligned'], t_aligned)
                SCS_stages[-1]['v_aligned'] = np.vstack([SCS_stages[-1]['v_aligned'], v_aligned])
                SCS_stages[-1]['vrms_aligned'] = np.vstack([SCS_stages[-1]['vrms_aligned'], vrms_aligned])

            # plt.plot(v_aligned)
            # plt.show()
        elif stage['Name'] == 'fp':
            for HCLop in stage['HCL operation points']:
                if HCLop['HCL state']['Regime'] == 'continuous':
                    hcl_on_time = HCLop['Time (s)']
                    HCL_current = HCLop['HCL state']['Current']
                    inv_polarity = HCLop['HCL state']['flipped polarity']
                    stage['inverted_polarity'] = inv_polarity

                elif HCLop['HCL state']['Regime'] == 'idle':
                    hcl_off_time = HCLop['Time (s)']
            
            for SCS_profile in stage['SCS profiles']:
                i_scs = SCS_profile['SCS no.']
                for SCSop in SCS_profile['SCS op']:
                    if SCSop['Duty-cycle (%)'] > 0:
                        s2_on_time = SCSop['Time (s)']

            if 'HCL_current' not in SCS_stages[-1].keys():
                SCS_stages[-1]['HCL_current'] = HCL_current

                        
            # hcl_on_sample_interval = (hcl_on_time + s1_recovery, hcl_off_time)
            hcl_on_sample_interval = (hcl_on_time + s1_recovery, s2_on_time)
            hcl_off_sample_interval = (hcl_off_time + s2_recovery, profile_length)
            
            t_refd = t_stage.copy()/1000
            # t_refd = np.mod(t_refd, stage['profile_length'])
            # t_off = []
            # t_on = []
            # v_off = []
            # v_on = []
            stage['hcl_off_data'] =  {'t': [t_0-t_shift], 'v': [v_0], 'vrms': [vrms_0]} if t_0 != None else {'t': [], 'v': [], 'vrms': []}
            stage['hcl_on_data'] = {'t': [], 'v': [], 'vrms': []}
            # if t_0 is  not None:
            #     stage['hcl_off_data'] =  {'t': [t_0-stage['t_shift']], 'v': [v_0]}
            
            for i_cycle in range(stage['# rep']):
                hcl_on_mask = np.array(t_refd >= hcl_on_sample_interval[0]) & np.array(t_refd < hcl_on_sample_interval[1])
                stage['hcl_on_data']['t'].append(np.mean(t_stage[hcl_on_mask]))
                stage['hcl_on_data']['v'].append(np.mean(v_stage[hcl_on_mask], axis=0))
                stage['hcl_on_data']['vrms'].append(np.std(v_stage[hcl_on_mask], axis=0))

                
                hcl_off_mask = np.array(t_refd >= hcl_off_sample_interval[0]) & np.array(t_refd < hcl_off_sample_interval[1])
                # _t = np.mean(t_refd[hcl_off_mask])
                stage['hcl_off_data']['t'].append(np.mean(t_stage[hcl_off_mask]))
                stage['hcl_off_data']['v'].append(np.mean(v_stage[hcl_off_mask], axis=0))
                stage['hcl_off_data']['vrms'].append(np.std(v_stage[hcl_off_mask], axis=0))
                
                t_refd -= profile_length
            stage['hcl_on_data']['t'] = np.array(stage['hcl_on_data']['t'])
            stage['hcl_on_data']['v'] = np.array(stage['hcl_on_data']['v'])
            stage['hcl_on_data']['vrms'] = np.array(stage['hcl_on_data']['vrms'])
            stage['hcl_off_data']['t'] = np.array(stage['hcl_off_data']['t'])
            stage['hcl_off_data']['v'] = np.array(stage['hcl_off_data']['v'])
            stage['hcl_off_data']['vrms'] = np.array(stage['hcl_off_data']['vrms'])
            
            # reset previous values
            t_0 = None
            v_0 = None
            vrms_0 = None

        elif stage['Name'] == 'flux_flush':
            for profile in stage['SCS profiles']:
                if profile['SCS no.'] == 1:
                    for op in profile['SCS op']:
                        if op['Duty-cycle (%)'] == 0:
                            t_flushed = op['Time (s)']
                            break

            mask_flushed = t_stage >= t_flushed*1000
            n_samples = np.count_nonzero(mask_flushed)
            t_flushed = np.mean(t_stage[mask_flushed])/1000
            v_flushed = v_stage[mask_flushed].mean(axis=0)
            vrms_flushed = v_stage[mask_flushed].std(axis=0)
            v_0 = v_flushed
            vrms_0 = vrms_flushed
            stage['t_flushed'] = t_flushed
            stage['v_flushed'] = v_flushed
            stage['vrms_flushed'] = vrms_flushed
            t_flushed += t_shift
            t_0 = t_flushed
            if 't_flushed' not in SCS_stages[-1].keys():
                SCS_stages[-1]['t_flushed'] = np.array([t_flushed])
                SCS_stages[-1]['v_flushed'] = np.array([v_flushed])
                SCS_stages[-1]['vrms_flushed'] = np.array([vrms_flushed])
                SCS_stages[-1]['n_samples_flushed'] = np.array([n_samples])

            else:
                SCS_stages[-1]['t_flushed'] = np.append(SCS_stages[-1]['t_flushed'], t_flushed)
                SCS_stages[-1]['v_flushed'] = np.vstack([SCS_stages[-1]['v_flushed'], v_flushed])
                SCS_stages[-1]['vrms_flushed'] = np.vstack([SCS_stages[-1]['vrms_flushed'], vrms_flushed])
                SCS_stages[-1]['n_samples_flushed'] = np.append(SCS_stages[-1]['n_samples_flushed'], n_samples)
    
        elif stage['Name'] == 'idle':
            # take sample from last 100 pts
            n_samples = 100
            SCS_stages[-1]['t_decay_h'] = profile_length/3600
            SCS_stages[-1]['v_decay'] = v_stage[-n_samples:,:].mean(axis=0)
            SCS_stages[-1]['vrms_decay'] = v_stage[-n_samples:,:].std(axis=0)
            SCS_stages[-1]['n_samples_decay'] = n_samples

    return SCS_stages

def analyse_flux_pumping_stages(filepath, doc_format='png'):
    t,v,metadata = get_hs_data(filepath)
    set_shimnames(metadata)
    # t,v,metadata2 = get_hs_data('test/scp_stages/HS_reading_old_metadata.csv')

    SCS_stages = metadata.get('SCS profiles', metadata.get('SCS stages', None))

    add_signal_to_SCS_stages(SCS_stages, t, v)
    analyse_flux_pumping(SCS_stages)

    savepath = filepath.replace('.csv', f'_pumping_stages.{doc_format}')
    plot_flux_pumping(SCS_stages, savepath=savepath)

def analyse_flux_pumping_stages_indir(dirpath, doc_format='png'):
    files = find_HS_reading_indir(dirpath)
    errors = []
    for file in files:
        try:
            print(f"Analyzing file: {file}")
            analyse_flux_pumping_stages(file, doc_format=doc_format)
        except Exception as e:
            errors.append((file, e))
    
    if errors:
        print("Errors occurred in the following files:")
        for file, error in errors:
            print(f"{file}: {error}")

def stage_pulse_analysis(SCS_stage):

    t = SCS_stage['t_orig'].copy()
    t_refd = SCS_stage['t'].copy()/1000
    v = SCS_stage['v'].copy()
    t_shift = SCS_stage['t_shift']
    HCL_ops = SCS_stage['HCL operation points']
    # Pumping coil operation points
    Pumping_coil_ops = SCS_stage['Pumping coil operation points']
    # TODO: preselect which ops are we analysing 
    # all_ops = HCL_ops + Pumping_coil_ops
    stage_current_controll_operation_points = [HCL_ops, Pumping_coil_ops]


    # n_op = len(all_ops)
    for ops in stage_current_controll_operation_points:
        for i_op, op in enumerate(ops):
            if op['HCL state']['Regime'] == 'pulsing':
                t_u = op['HCL state']['Pulse timing']['up time']*1e3
                t_d = op['HCL state']['Pulse timing']['down time']*1e3
                
                if i_op == len(ops)-1:
                    interval_mask = t_refd >= op['Time (s)']
                else:
                    # this is case for multiple pulsing ops 
                    interval_mask = np.array(t_refd >= op['Time (s)']) & np.array(t_refd < ops[i_op + 1]['Time (s)'])

                _t = t[interval_mask]
                _v = v[interval_mask]
                    

                pulse_analysis = analyse_pulses(_t, _v, t_u,t_d, pedestal_fit_order=0)
                op['pulse_analysis'] = pulse_analysis.copy()
            # plt.subplot(3,1,1)
            # plt.plot(pulse_analysis['pulse_time'], pulse_analysis['pulse_height'])
            # plt.subplot(3,1,2)
            # plt.plot(_t,_v)
            # plt.subplot(3,1,3)
            # plt.plot(t,v)
            # plt.show()
    # return pulse_analysis

def analyse_pumping_cycle_scan_stages(filepath, doc_format='png'):
    t,v,metadata = get_hs_data(filepath)
    set_shimnames(metadata)

    SCS_stages = metadata.get('SCS profiles', metadata.get('SCS stages', None))
    SCS_stages.append({'Name': 'analysis'})

    t_shift = 0
    _t = t.copy()
    _v = v.copy()
    for i_stage, stage in enumerate(SCS_stages):
        if stage['Name'] == 'analysis': continue

        stage['t_shift'] = t_shift
        
        profile_length = 0.
        # find longest profile in stage = profile length
        for profile in stage['SCS profiles']:
            for op in profile['SCS op']:
                profile_length = max(profile_length, op['Time (s)'])

        stage_length = stage['# rep'] * profile_length
        t_shift += stage_length
        stage['profile_length'] = profile_length
        stage['stage_length'] = stage_length

        t_stage = _t[_t <= stage_length*1000]
        stage['t'] = t_stage
        _t = _t[_t > stage_length] - stage_length

        v_stage = _v[:len(t_stage),:]
        stage['v'] = v_stage

def analyse_pumping_cycle_scan(SCS_stages, shims_to_plot = []):
    parsed_fp_tuning_profiles = {'pre':{}, 'norm':{}}
    for stage in SCS_stages:
        stage_pulse_analysis(stage)   
        if stage['Name'] == 'warmup':
            for key, item in parse_SCS_profiles_from_stage(stage).items():
                parsed_fp_tuning_profiles['pre']['PRE'+key] = item
            pulse_analysis_warmup = stage['HCL operation points'][0]['pulse_analysis']
            warmup_length = stage['stage_length']
            v_warmup = stage['v']
            t_warmup = stage['t']
            # plt.plot(t_warmup, v_warmup - v_warmup[0])
            # plt.show()

        if stage['Name'] in ['fpc_tuning', 'single_scs_pulse']:
            for key, item in parse_SCS_profiles_from_stage(stage).items():
                parsed_fp_tuning_profiles['norm'][key] = item
            
            stage_current_controll_operation_points = [
                stage.get('HCL operation points', None),
                stage.get('Pumping coil operation points', None),
                                    
            ]
            for sop in stage_current_controll_operation_points:
                pulse_analysis = sop[0].get('pulse_analysis', False)
                if pulse_analysis:
                    break

            
            t = stage['t'].copy()
            v = stage['v'].copy()

            if parsed_fp_tuning_profiles['pre']:
                pulse_analysis['pulse_height'] = np.vstack([pulse_analysis_warmup['pulse_height'], pulse_analysis['pulse_height']])
                v = np.vstack([v_warmup, v])
                # pulse_analysis['pulse_time'] = np.append(pulse_analysis_warmup['pulse_time'], pulse_analysis['pulse_time'])
                pulse_analysis['pulse_time'] = np.append(pulse_analysis_warmup['pulse_time'], pulse_analysis['pulse_time'])
                t = np.append(t_warmup, t + warmup_length*1000)

    if not parsed_fp_tuning_profiles['pre']: parsed_fp_tuning_profiles.pop('pre')
    return t,v,parsed_fp_tuning_profiles,pulse_analysis

def analyse_pumping_cycle_scan_stages(filepath, doc_format='png'):
    t, v, metadata = get_hs_data(filepath)
    set_shimnames(metadata)
    SCS_stages = metadata.get('SCS profiles', metadata.get('SCS stages', None))
    add_signal_to_SCS_stages(SCS_stages, t, v)

    filepath = filepath.replace('.csv', '_fpc_scan.' + doc_format)
    plot_SCS_profile_with_repetitions(*analyse_pumping_cycle_scan(SCS_stages), savepath= filepath)

def analyse_stages(filepath, shims_to_plot = [], doc_format='png', plot=True):
    fname = filepath.replace('.csv','')
    t, v, metadata = get_hs_data(filepath)
    set_shimnames(metadata)
    
    SCS_stages = metadata.get('SCS profiles', metadata.get('SCS stages', None))
    
    add_signal_to_SCS_stages(SCS_stages, t, v)
    stages_list = [item['Name'] for item in SCS_stages]

    if 'fpc_tuning' in stages_list or 'single_scs_pulse' in stages_list:
        if plot:
            cycle_analysis = analyse_pumping_cycle_scan(SCS_stages)
            scb_analysis = analyse_scb(SCS_stages)
            t,v,parsed_fp_tuning_profiles,pulse_analysis = cycle_analysis # TODO: make plot_SCS_profile_with_repetitions to figure out these values from SCS_stages
            plot_pulse_height_histogram(pulse_analysis, savepath=fname+f'_pulse_height_histogram.{doc_format}')
            plot_SCS_profile_with_repetitions(*cycle_analysis, savepath= fname+f'_fpc_scan.{doc_format}')

        else: 
            analyse_pumping_cycle_scan(SCS_stages)
    if 'fp' in stages_list:
        # savepath = filepath.replace('.csv', f'_pumping_stages.{doc_format}')
        if plot:
            plot_flux_pumping(analyse_flux_pumping(SCS_stages), fname+f'_pumping.{doc_format}')
        else:
            analyse_flux_pumping(SCS_stages)

    # if 'single_scs_pulse' in stages_list:
    #     if plot:
    #         plot_SCS
    if plot:
        subplot_hs_signal(t,v, savepath=fname+f'_signal.{doc_format}', dpi = 250)
    # plot_stages_hs_signal(SCS_stages)

    return SCS_stages


def analyse_stages_indir(dirpath, shims_to_plot = [],doc_format='png', walk = True):

    files = find_HS_reading_indir(dirpath) if walk else get_HS_reading_indir(dirpath)
    errors = []
    n_files = len(files)
    for i, file in enumerate(files):
        try:
            print(f"\nAnalyzing file: ({i+1}/{n_files}) {file} ")
            analyse_stages(file, doc_format=doc_format)

            gc.collect()

        except Exception as e:
            errors.append((file, e))
    
    if errors:
        print("Errors occurred in the following files:")
        for file, error in errors:
            print(f"{os.path.abspath(file)}: {error}")

def analyse_hcl_current_effect_on_pumping(dirpath, doc_format='png'):
    files = get_HS_reading_indir(dirpath)
    errors = []
    n_ch = 0
    analyses = []
    for file in files:
        try:
            print(f"Analyzing file: {file}")
            # fname = file.replace('.csv','')
            t, v, metadata = get_hs_data(file)
            n_ch = max(n_ch, v.shape[1])
            SCS_stages = metadata.get('SCS profiles', metadata.get('SCS stages', None))
            add_signal_to_SCS_stages(SCS_stages, t, v)
            analyse_flux_pumping(SCS_stages)
            analyses.append(SCS_stages)
            
            # get used pumping current


            # analyse_stages(file, doc_format=doc_format)
        except Exception as e:
            errors.append((file, e))  

    set_shimnames(metadata)

    plot_pumping_vs_hcl_current(analyses, os.path.join(dirpath, 'pumping_VS_HCL-current.'+doc_format))

def analyse_flux_decay(dirpath, doc_format='png'):
    t_decay = []
    v_decay_flush_difference = []
    vrms_decay_flush_difference = []
    for HS_reading_file in find_HS_reading_indir(dirpath):

        SCS_profiles = analyse_stages(HS_reading_file, plot= False)
        analysis = SCS_profiles[-1]

        t_decay.append(analysis['t_decay_h'])
        v_decay_flush_difference.append(analysis['v_decay'] - analysis['v_flushed'][-1])
        reduced_std_sq_decay = analysis['vrms_decay']**2/analysis['n_samples_decay']
        reduced_std_sq_flushed = analysis['vrms_flushed'][-1]**2/analysis['n_samples_flushed'][-1]

        vrms_decay_flush_difference.append(np.sqrt(reduced_std_sq_decay + reduced_std_sq_flushed))
    v_decay_flush_difference = np.array(v_decay_flush_difference)
    vrms_decay_flush_difference = np.array(vrms_decay_flush_difference)
    
    plot_flux_decay(t_decay, v_decay_flush_difference, vrms_decay_flush_difference, os.path.join(dirpath, 'decay_measurement.' + doc_format))

def get_rep_stage_pulse_analysis_averaged(filepath):
    fname = filepath.replace('.csv','')

    SCS_stages = analyse_stages(filepath, plot=False)



    

    # n_ch = pulse_analysis['pulse_height'].shape[1]
    SCS_stage = SCS_stages[0]
    

    stage_current_controll_operation_points = [
        SCS_stage.get('HCL operation points', None),
        SCS_stage.get('Pumping coil operation points', None),                            
    ]

    for sop in stage_current_controll_operation_points:
        pulse_analysis = sop[0].get('pulse_analysis', False)
        if pulse_analysis:
            break
    
    # pulse_analysis = SCS_stage['HCL operation points'][0]['pulse_analysis']
    # pulse_analysis_histogram = get_pulse_analysis_histogram(pulse_analysis, bins=50)
    
    SCS_profile_period = get_SCS_profile_period(SCS_stage['SCS profiles'])
    pulse_time = pulse_analysis['pulse_time']
    pulse_height = pulse_analysis['pulse_height']

    pulse_time, pulse_height = split_arrays_by_period(pulse_time, SCS_profile_period*1e3, pulse_height)

    # make sure all repetitions have the same length

    min_length = min([len(ar) for ar in pulse_time])
    pulse_time = np.array([rep_time[:min_length] for rep_time in pulse_time])
    # pulse_time = pulse_time[:min_length]
    pulse_height = np.array([rep_height[:min_length,:] for rep_height in pulse_height])
    
    # average pulse height over repetitions
    pulse_height_avg = np.nanmean(pulse_height, axis=0)
    pulse_height_std = np.nanstd(pulse_height, axis=0)
    # plt.plot(pulse_time[0], pulse_height_avg)
    
    # for ch in range(pulse_height_avg.shape[1]):
    #     plt.plot(pulse_time[0], pulse_height_avg[:,ch], label=f'Ch {ch+1}')
    #     plt.fill_between(pulse_time[0], pulse_height_avg[:,ch] - pulse_height_std[:,ch], pulse_height_avg[:,ch] + pulse_height_std[:,ch], alpha=0.3)
        
    # plt.show()
    SCS_profiles = parse_SCS_profiles_from_stage(SCS_stage)

    return pulse_time, pulse_height_avg, pulse_height_std, SCS_profiles, METADATA[0]


def analyse_rep_pulses(dirpaths, doc_format='png', rewrite=False):
    files = []
    if isinstance(dirpaths, str):
        dirpaths = [dirpaths]
    for dirpath in dirpaths:
        files += get_HS_reading_indir(dirpath)
    results = []
    errors = []
    for file in files:
        try:
            print(f"Analyzing file: {file}")
            pulse_time, pulse_height_avg, pulse_height_std, SCS_profiles, metadata = get_rep_stage_pulse_analysis_averaged(file)
            fname = file.replace('.csv','')
            results.append({'pulse_time':pulse_time, 'pulse_height_avg':pulse_height_avg, 'pulse_height_std':pulse_height_std, 'SCS_profiles':SCS_profiles, 'metadata':metadata})
            # plot_rep_pulses(pulse_time[0], pulse_height_avg, pulse_height_std, SCS_profiles, savepath=fname+f'_rep_pulses.{doc_format}')
        except Exception as e:
            errors.append((file, e))
    
    
    dirpath = dirpaths[0]
    filename_default_root = 'averaged_rep_stage_pulses'
    filename_root = filename_default_root
    file_index = 0
    if not rewrite:
        # check if averaged_rep_stage_pulses file already exists
        while os.path.exists(os.path.join(dirpath, f'{filename_root}.{doc_format}')):
            file_index += 1
            filename_root = f'{filename_default_root}_{file_index}'

    plot_averaged_rep_stage_pulses(results, savepath=os.path.join(dirpath, f'{filename_root}.{doc_format}'))

    if errors:
        print("Errors occurred in the following files:")
        for file, error in errors:
            print(f"{file}: {error}")


# files = get_HS_reading_indir('mount/single_scs1_pulse-P_current_scan/3V2pp')
# results = []
# for file in files:
#     pulse_time, pulse_height_avg, pulse_height_std, SCS_profiles, metadata = get_rep_stage_pulse_analysis_averaged(file)
def analyse_scb(SCS_stages):
    SCS_stage = SCS_stages[0]
    stage_current_controll_operation_points = [
        SCS_stage.get('HCL operation points', None),
        SCS_stage.get('Pumping coil operation points', None),                            
    ]

    for sop in stage_current_controll_operation_points:
        pulse_analysis = sop[0].get('pulse_analysis', False)
        if pulse_analysis:
            break

    pulse_analysis_histogram = get_pulse_analysis_histogram(pulse_analysis, bins=50)
    
    return pulse_analysis_histogram


def get_pulse_analysis_histogram(pulse_analysis, bins=50):
    # pulse_analysis = SCS_stage['HCL operation points'][0]['pulse_analysis']
    
    
    pulse_height = pulse_analysis['pulse_height']
    pulse_time = pulse_analysis['pulse_time']

    # flatten pulse height and time
    pulse_height_flat = pulse_height.flatten()
    pulse_time_flat = np.tile(pulse_time, (pulse_height.shape[1], 1)).T.flatten()

    # remove NaN values
    mask = ~np.isnan(pulse_height_flat)
    pulse_height_flat = pulse_height_flat[mask]
    pulse_time_flat = pulse_time_flat[mask]

    hist, bin_edges = np.histogram(pulse_height_flat, bins=bins)
    
    return hist, bin_edges, pulse_time_flat, pulse_height_flat
