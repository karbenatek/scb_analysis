
import pandas as pd
import numpy as np
import ast, os
from parser import get_metadata, get_header
# import gc_utils.info as info
# from gc_utils.parser import get_metadata
from sc_break import  SHIM_ORDER, SHIM_CHANNELS, SHIM13_ORDER, METADATA

def get_hs_data(filepath):
    # read csv file, skip first row
    header = get_header(filepath)

    df = pd.read_csv(filepath)
    # print(header)
    # exit()
    # get time and voltage columns
    
    ## old method
    # header_list = df.columns.tolist()
    # for i, item in enumerate(header_list):
    #     if 'metadata' in item:
    #         header_list = header_list[:i]
    #         break
    # n_ch = len( [s for s in header_list if 'ch' == s[:2]] )
    
    n_ch = get_number_of_channels(header)

    
    time = df.iloc[:, 0].to_numpy()
    voltage = df.iloc[:, 1:n_ch+1].to_numpy().transpose()
    metadata = get_metadata(header)

    # rewrite global metadata
    METADATA[0] = metadata
    get_HCL_info(metadata)

    return time, voltage, metadata

def get_number_of_channels(header):
    # header = df.columns.tolist()
    n_ch = 0
    for s in header.split(','):
        if 'metadata' in s:
            break
        elif 'ch' == s[:2]:
            n_ch += 1
        
    # n_ch = len( [s for s in header_list if 'ch' == s[:2]] )
    return n_ch

# extract HCL configuration parameters
def get_HCL_info(metadata = ""):
    if not metadata:
        metadata = METADATA[0]
    if isinstance(metadata['HCL'], str):
        HCLinfo = metadata['HCL']
        _HCLinfo = HCLinfo.split(',')
        HCLinfo = {}
        for item in _HCLinfo:
            key, val = item.split('=')
            HCLinfo[key] = float(val)
        metadata['HCL'] = HCLinfo
        METADATA[0] = metadata
        return HCLinfo
    
    else:
        return metadata['HCL']


def get_SCS_info(metadata = ""):
    if not metadata:
        metadata = METADATA[0]
    if isinstance(metadata['scs'], str):
    
        SCSinfo = metadata['scs']
        _SCSdata = SCSinfo.split(',')
        SCSinfo = {}
        for item in _SCSdata:
            key, val = item.split('=')
            SCSinfo[key] = int(val) if key in ['i'] else float(val)  
        metadata['scs'] = SCSinfo
        METADATA[0] = metadata
        return SCSinfo
    else:
        return metadata['scs']

def get_CH_info(metadata = ""):
    if not metadata:
        metadata = METADATA[0]
    if isinstance(metadata['channels'], str):
        CHinfo = metadata['channels']
        CHinfo = list(ast.literal_eval(CHinfo))

        metadata['channels'] = CHinfo
        METADATA[0] = metadata
        return CHinfo
    
    else:
        return metadata['channels']
# if __name__ == "__main__":
#     metadata = {'time': '28-01-26_10-44-17', 'readout': 'chop_type=2,n_chop=2,res=0,cur=3.10,DOtime=10', 'channels': '[2,1,0],[0,1,2]', 'scs': {'i': 6, 'Vpp': 3.0, 'f': 3000.0, 'h': 400.0, 'c': 200.0}, 'HCL': {'I': 3.0, 'd': 15.0, 'u': 1.0}, 'T': '65K'}
#     print(get_CH_info(metadata))
#     exit(0)

def set_shimnames(metadata):
    reset_shimnames()
    shim_order = []
    if 'channels' in metadata.keys():
        shim_selection = [SHIM_ORDER[:len(SHIM_CHANNELS[0])],SHIM_ORDER[len(SHIM_CHANNELS[0]):]]
        # print(metadata['channels'])
        # convert to arrays
        # print(shim_selection)
        if isinstance(metadata['channels'], str):
            channels = ast.literal_eval(metadata['channels'])
        else:
            channels = metadata['channels']
        for i_daq, chans in enumerate(channels):
            for chan in chans:
                # get index of channel
                i_chan = SHIM_CHANNELS[i_daq].index(chan)
                shim_order.append(shim_selection[i_daq][i_chan])

        for i,shim_name in enumerate(shim_order):

            SHIM_ORDER[i] = shim_name

    return shim_order

def reset_shimnames():
    SHIM_ORDER.clear()
    for shimname in SHIM13_ORDER:
        SHIM_ORDER.append(shimname)
    
def save_pulse_analysis_data(pulse_analysis, filepath):
    # with  open(filepath, 'w') as f:
        # write header
        # f.write('time (ms),(mV)\n')
        # for idle_time, pulse_height in zip(pulse_analysis['pulse_time'], pulse_analysis['pulse_height']):
        #     f.write(f"{idle_time},{pulse_height}\n")
        # }
    channels = get_CH_info()

    time = pulse_analysis['pulse_time']
    voltage = pulse_analysis['pulse_height']
    with open(filepath, 'w') as f:
        # write header
        num_channels = voltage.shape[1]
        header = ','.join([f'ch{i+1} [mV]' for i in range(num_channels)]) + ',metadata=[channels=' + str(channels) + ']'
        print(header)
        f.write(f'time [ms],{header}\n')
        for time_val, voltages in zip(time, voltage):
        
            if np.isnan(time_val):
                continue
            voltage_str = ','.join([f'{v:.4f}' for v in voltages])
            f.write(f'{int(time_val)},{voltage_str}\n')
        print(f"Saved pulse analysis data to: {filepath}")

def read_pulse_analysis_data(filepath):
    header = get_header(filepath)

    metadata = get_metadata(header)
    CH_info = get_CH_info(metadata)
    n_ch = get_number_of_channels(header)


    for item in os.path.basename(filepath).split('_'):
        if 'VPP=' in item:
            Vpp = float(item.replace('VPP=',''))
            break
    df = pd.read_csv(filepath)
    time = df.iloc[:, 0].to_numpy()
    voltage = df.iloc[:, 1:n_ch+1].to_numpy()
    pulse_analysis = {'time': time, 'pulses': voltage.T, 'Vpp': Vpp, 'channels': CH_info, 'filepath': filepath}
    
    return pulse_analysis
# metadata=[time=09-12-25_18-05-23,readout=[chop_type=2,n_chop=2,res=0,cur=2.00,DOtime=5],scs=[i=4,Vpp=3.500,f=3000,h=400],HCL=0.500000]