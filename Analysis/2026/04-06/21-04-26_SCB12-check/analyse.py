from utils import *
import os
import gc_utils.info as info
from sc_break.analysis import analyse_scba_indir #, analyse_scba
import hcl_pulse.analysis as hcl_pulse


# analyse_scba_indir('mount/data/')
# analyse_scba('data/')
csv_files = [f for f in os.listdir('mount/pulses') if f.endswith('.csv')]
print(csv_files)
for file in csv_files[1:]:
    hcl_pulse.sequence_analysis('mount/pulses/' + file)
# hcl_pulse.sequence_analysis('mount/pulses/HCL-response_time=21-04-26_16-27-06.csv')