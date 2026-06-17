import site
from utils import *
# from hcl_pulse.parser import parse_config_string, get_hcl_pulse_data
import hcl_pulse.analysis as hcl_pulse
import gc_utils.info as info
# from hcl_pulse.plotter import plot_hcl_pulses

measurements = {
    '50K': 'mount/50K/',
    '100K': 'mount/100K/',
    '150K': 'mount/150K/',
    'room temp': 'mount/room temp/'}

# print(this_dir)



for meas, dirpath in measurements.items():
    print(f"Measurement: {meas}")
    # get files in directory
    files = os.listdir(dirpath)
    # filter .csv
    files = [f for f in files if f.endswith('.csv')]
    # get full paths
    files = [dirpath + f for f in files]
    
    for file in files:
        # make a plot
        hcl_pulse.sequence_analysis(file, label=meas)
            