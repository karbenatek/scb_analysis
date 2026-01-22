from hcl_pulse.parser import get_hcl_pulse_data, read_pulse_sequence_info
from hcl_pulse.plotter import plot_hcl_pulses, plot_hcl_pulses_signal
import os
import numpy as np
import gc_utils.info as info


def sequence_analysis(filepath, label=None):
    # get filename
    print("Pulse sequence analysis on file:", filepath)
    ps_info = info.read().get('pulse_sequence', { 't_offset': 0, 't_e': 0 })
    
    
    filename = os.path.basename(filepath)
    # cfg = parse_config_string(filename.replace('.csv', ''))
    time, voltage, cfg, metadata = get_hcl_pulse_data(filepath)
    if not label:
        label = metadata.get('T', '')
        if label[-1] != 'K': label += 'K'
        
    time += ps_info['t_offset']
    
    # print("Analysis info:", info)
    high_time = cfg['u']
    down_time = cfg['d']
    
    sequence = cfg['pulse_sequence']
    n_pulses = len(sequence)
    t_e = ps_info['t_e']
    
    intervals = []
    pulse_height = []
    pulse_error = []
    for i in range(n_pulses):
        # print(f" Pulse {i+1}: {sequence[i]} V")
        t0 = i * (high_time + down_time)
        down_start = t0 + high_time if i > 0 else 0
        down_end = t0 + down_time - t_e
        rising_edge = t0 + down_time
        high_start = rising_edge + t_e
        high_end = high_start + high_time - 2*t_e
        falling_edge = high_end + t_e
        
        intervals.append((down_start, down_end, rising_edge, high_start, high_end, falling_edge))
        pedestal_time = down_time / 2
        pedestal_interval = (t0 + pedestal_time, t0 + down_time - t_e)
        pedestal_mean = np.mean(voltage[:, (time >= pedestal_interval[0]) & (time < pedestal_interval[1])], axis=1)
        pulse_mean = np.mean(voltage[:, (time >= high_start) & (time < high_end)], axis=1)
        pulse_std = np.std(voltage[:, (time >= high_start) & (time < high_end)], axis=1)
        pulse_error.append(pulse_std)
        pulse_height.append(pulse_mean - pedestal_mean)
    # print(" Pulse heights (mV):", pulse_height)
    pulse_height = np.array(pulse_height).T
    pulse_error = np.array(pulse_error).T
    
    # subtract pedestal
    for volt in voltage:
        
        pedestal = np.mean(volt[time < down_time/2])
        volt -= pedestal
        
    plot_hcl_pulses_signal(time, voltage, cfg, intervals=intervals, savepath=filepath.replace('.csv', '_signal.png'), label=label)
    plot_hcl_pulses(sequence, pulse_height, pulse_error, cfg, savepath=filepath.replace('.csv', '_pulses.png'), label=label)
    
def sequence_analysis_indir(dirpath):
    # get files in directory
    files = os.listdir(dirpath)
    # filter .csv
    files = [f for f in files if f.startswith('HCL-response_') and f.endswith('.csv')]
    # get full paths
    files = [dirpath + f for f in files]
    
    for file in files:
        # make a plot
        sequence_analysis(file)
