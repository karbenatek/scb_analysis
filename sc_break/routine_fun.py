import os

from sc_break import info, np

def get_SCS_profile_rising_edge_times(SCS_profiles):
    rising_edges = {}
    for key, profile in SCS_profiles['norm'].items():
        rising_edges[key] = []
        # figure out whether firs value is rising edge
        if profile[0][1] > profile[1][1] or profile[0][1] > 0:
            rising_edges[key].append(profile[0])
        for i in range(1, len(profile)-1):
            if profile[i][1] > profile[i-1][1]:
                rising_edges[key].append(profile[i])

    return rising_edges

def get_SCS_profile_falling_edge_times(SCS_profiles):
    falling_edges = {}
    for key, profile in SCS_profiles['norm'].items():
        falling_edges[key] = []
        # figure out whether firs value is falling edge
        if profile[0][1] < profile[1][1] or profile[0][1] < 0:
            falling_edges[key].append(profile[0])
        for i in range(1, len(profile)-1):
            if profile[i][1] < profile[i-1][1]:
                falling_edges[key].append(profile[i])

    return falling_edges

def get_SCS_profile_all_edges_times(SCS_profiles):
    all_edges = {}
    for key, profile in SCS_profiles['norm'].items():
        all_edges[key] = []
        # figure out whether firs value is rising edge or falling edge
        if profile[0][1] > profile[1][1] or profile[0][1] > 0:
            all_edges[key].append(profile[0])
        elif profile[0][1] < profile[1][1] or profile[0][1] < 0:
            all_edges[key].append(profile[0])
        for i in range(1, len(profile)-1):
            if profile[i][1] > profile[i-1][1]:
                all_edges[key].append(profile[i])
            elif profile[i][1] < profile[i-1][1]:
                all_edges[key].append(profile[i])

    return all_edges

def get_SCS_profile_period(SCS_profiles):
    last_values = [0]
    if isinstance(SCS_profiles, dict):
        SCS_profiles_length = [SCS_op[-1][0] for SCS_op in list(SCS_profiles['norm'].values())]
    else:
        SCS_profiles_length = [ [SCS_op['Time (s)'] for SCS_op in SCS_profile['SCS op']][-1] for SCS_profile in SCS_profiles]

    for profile_length in SCS_profiles_length:
        last_values.append(profile_length)
    return np.max(last_values)

def get_PRESCS_profile_length(SCS_profiles):
    last_values = []
    if 'pre' not in SCS_profiles:
        return 0
    for key, profile in SCS_profiles['pre'].items():
        last_values.append(profile[-1][0])
    return np.max(last_values)

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

def split_arrays_by_period(time, period, *arrays):
    """
    Splits time and provided arrays into chunks based on the given period.
    Each chunk is time-referenced to zero (modulo period).
    
    Parameters:
    - time: 1D array of time values
    - period: the period to split by
    - *arrays: any number of arrays (1D or 2D) with first dimension matching time
    
    Returns:
    - time_chunks: list of time chunks (each chunk is time % period)
    - *array_chunks: lists of chunks for each input array, in the same order
    """
    referenced_time = np.mod(time, period)
    
    time_chunks = []
    array_chunks = [[] for _ in arrays]
    
    i_0 = 0
    for i, t in enumerate(referenced_time):
        if i == 0:
            continue
        if referenced_time[i-1] > referenced_time[i]:
            time_chunks.append(referenced_time[i_0:i-1])
            for j, arr in enumerate(arrays):
                array_chunks[j].append(arr[i_0:i-1])
            i_0 = i
    
    # Add the last chunk
    if i_0 < len(time):
        time_chunks.append(referenced_time[i_0:])
        for j, arr in enumerate(arrays):
            array_chunks[j].append(arr[i_0:])
    
    return time_chunks, *array_chunks

def chop_preparation(time, prep_length, voltage, followup_in_prep=True):
    """
    Splits time and voltage arrays into preparation part (before first period) and main part (after first period).
    
    Parameters:
    - time: 1D array of time values
    - prep_length: the preparation time to split by
    - voltage: 2D array of voltage values with first dimension matching time
    
    Returns:
    - prep_time: time values before the first period
    - prep_voltage: voltage values before the first period
    - main_time: time values after the first period
    - main_voltage: voltage values after the first period
    """
    # referenced_time = np.mod(time, prep_length)
    
    i_0 = 0
    for i in range(1, len(time)):
        if time[i] > prep_length:
            i_0 = i
            break
    
    prep_time = time[:i_0+1] if followup_in_prep else time[:i_0]
    prep_voltage = voltage[:i_0+1] if followup_in_prep else voltage[:i_0]
    
    main_time = time[i_0:] - prep_length
    main_voltage = voltage[i_0:]
    
    return prep_time, prep_voltage, main_time, main_voltage

def find_HS_reading_indir(dirpath):
    # get all files in directory and subdirectories that start with HS_reading_ and end with .csv
    files = []
    dirs_to_ignore = []
    for root, dirs, filenames in os.walk(dirpath):
        # ignore hidden directories
        dirs_to_ignore += [os.path.join(root, d) for d in dirs if d.startswith('.')]
        for filename in filenames:
            if filename.startswith('HS_reading_') and filename.endswith('.csv') and 'pulse_analysis' not in filename: 
                if root not in dirs_to_ignore:
                    files.append(os.path.join(root, filename))

    return files


def get_HS_reading_indir(dirpath):
    files = []
    for filename in os.listdir(dirpath):
        if filename.startswith('HS_reading_') and filename.endswith('.csv') and 'pulse_analysis' not in filename: 
            # append absolute path
            files.append(os.path.abspath(os.path.join(dirpath, filename)))
    return files