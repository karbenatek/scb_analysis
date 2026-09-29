
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
    df = pd.read_csv(filepath, skiprows=1, header=None)
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
    voltage = df.iloc[:, 1:n_ch+1].to_numpy()
    
    if voltage.shape[0] != time.shape[0]:
        if voltage.shape[1] == time.shape[0]:
            voltage = voltage.T
        else:
            raise ValueError("voltage's time dimension must match the length of time (either axis 0 or 1)")
    metadata = get_metadata(header)

    # rewrite global metadata
    get_HCL_info(metadata)
    METADATA[0] = metadata

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
    if isinstance(metadata.get('HCL', None), str):
        HCLinfo = metadata['HCL']
        _HCLinfo = HCLinfo.split(',')
        HCLinfo = {}
        for item in _HCLinfo:
            key, val = item.split('=')
            HCLinfo[key] = float(val)
        metadata['HCL'] = HCLinfo
        METADATA[0] = metadata
        return HCLinfo
    
    # case for a measurement with single SCS stage 
    elif len(metadata.get('SCS stages', None)) == 1:
        HCL_ops = metadata['SCS stages'][0]['HCL operation points']
        if len(HCL_ops) == 1:
            HCLinfo = HCL_ops[0]['HCL state']
        METADATA[0] = metadata
        return HCLinfo
    
    else:
        return metadata.get('HCL', None)


def parse_tuple_list(value):
    parsed = value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    if isinstance(parsed, (list, tuple)):
        try:
            return np.array(parsed, dtype=float)
        except (ValueError, TypeError):
            try:
                return np.array([[float(v) for v in item] for item in parsed], dtype=float)
            except Exception:
                return value

    return value


def get_SCS_info(metadata = ""):
    if not metadata:
        metadata = METADATA[0]
    # if (not isinstance(metadata, dict) or 'scs' not in metadata) :
    #     return {'i': 0, 'Vpp': 0, 'f': 0, 'h': 0, 'c': 0}
    
    if 'scs' in metadata: # check if 'scs' key exists - this is case for SCBA data
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
        
    # extract SCS profiles if any
    SCSs_w_profiles = []
    PRESCS_profiles = []

    for key in metadata.keys():
        if 'SCS' in key[:3] and len(key) > 3 and key[3:].isdigit(): # check if any key contains 'SCS' and the next char is a digit
            SCSs_w_profiles.append(key)
        if 'PRESCS' in key[:6] and len(key) > 6 and key[6:].isdigit(): # check if any key contains 'PRESCS' and the next char is a digit
            PRESCS_profiles.append(key)

    
    SCS_profiles = {}
    if SCSs_w_profiles: # if there are any keys that match the pattern
        SCS_profiles['norm'] = {}
        for key in SCSs_w_profiles:
            SCS_profiles['norm'][key] = parse_tuple_list(metadata[key])
        metadata['SCS_profiles'] = SCS_profiles
        METADATA[0] = metadata
    if PRESCS_profiles: # if there are any keys that match the pattern
        SCS_profiles['pre'] = {}
        for key in PRESCS_profiles:
            SCS_profiles['pre'][key] = parse_tuple_list(metadata[key])
        metadata['SCS_profiles'] = SCS_profiles
        METADATA[0] = metadata

    if 'SCS_FG' in metadata: # check if 'SCS_FG' key exists - this is case for SCS profile data
        if isinstance(metadata['SCS_FG'], str):
            SCSinfo = metadata['SCS_FG']
            _SCSdata = SCSinfo.split(',')
            SCSinfo = {}
            for item in _SCSdata:
                key, val = item.split('=')
                SCSinfo[key] = int(val) if key in ['i'] else float(val)
            metadata['SCS_FG'] = SCSinfo
            METADATA[0] = metadata
            return SCSinfo
        else:
            return metadata['SCS_FG']
        

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
    shim_selection = [SHIM_ORDER[:len(SHIM_CHANNELS[0])],SHIM_ORDER[len(SHIM_CHANNELS[0]):]]
    if 'channels' in metadata.keys():
    
        # print(metadata['channels'])
        # convert to arrays
        # print(shim_selection)
        if isinstance(metadata['channels'], str):
            channels = ast.literal_eval(metadata['channels'])
        else:
            channels = metadata['channels']
    elif 'HS readout cfg' in metadata.keys():
        channels = []
        for HS_cfg in metadata['HS readout cfg']:
                channels.append(HS_cfg['channels'])
    else:
        raise ValueError("No channel information found in metadata")
    
    for i_daq, chans in enumerate(channels):
        for chan in chans:
            # get index of channel
            if chan in SHIM_CHANNELS[i_daq]:
                i_chan = SHIM_CHANNELS[i_daq].index(chan)
                shim_order.append(shim_selection[i_daq][i_chan])
            else:
                i_chan = -1
                shim_order.append("U")

    for i,shim_name in enumerate(shim_order):

        SHIM_ORDER[i] = shim_name
    # remove remaining shim names
    for _ in range(len(shim_order), len(SHIM_ORDER)):
        SHIM_ORDER.pop()
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


def parse_SCS_profiles_from_stage(SCS_stage):
    out_profiles = {}
    SCS_profiles = SCS_stage['SCS profiles']
    for profile in SCS_profiles:
        out_profiles['SCS%i'%profile['SCS no.']] = []
        for op in profile['SCS op']:
            pt = [op['Time (s)'], op['Duty-cycle (%)']]
            out_profiles['SCS%i'%profile['SCS no.']].append(pt)
        out_profiles['SCS%i'%profile['SCS no.']] = np.array(out_profiles['SCS%i'%profile['SCS no.']])
    return out_profiles
