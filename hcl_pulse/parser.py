import pandas as pd
import numpy as np
from parser import get_metadata

def parse_pulse_cfg(metadata):
  
    s = metadata.split(',')
    pulse_cfg = {}
    
    pulse_cfg['d'] = int(s[0].split('=')[1])  # down time in ms
    pulse_cfg['u'] = int(s[1].split('=')[1])  # up time in ms
    pulse_cfg['pulse_sequence'] = [float(v) for v in s[2].split('-')]  # pulse sequence currents
            
    return pulse_cfg



def get_hcl_pulse_data(filepath):
    # read csv file, skip first row
    df = pd.read_csv(filepath)
    
    # get time and voltage columns
    # print(df)
    n_ch = len( [s for s in df.columns.tolist() if 'ch' == s[:2]] )
    
    
    time = df.iloc[:, 0].to_numpy()
    voltage = df.iloc[:, 1:n_ch+1].to_numpy().transpose()
    metadata = get_metadata(df)
    cfg = parse_pulse_cfg(metadata['pulses'])
    
    return time, voltage, cfg, metadata

def read_pulse_sequence_info():
    info = read_info()
    if not info or 'pulse_sequence' not in info:
        print("❌ No pulse sequence info found.")
        return None
    return info['pulse_sequence']