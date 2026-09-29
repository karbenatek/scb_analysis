from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_scba_indir, analyse_scba, find_and_analyse_scs_profiles

# analyse_scba_indir('mount/data/')
# analyse_scba('mount/SCS1/HS_reading_time=11-05-26_18-40-50.csv')
find_and_analyse_scs_profiles('mount/11-05-26_SCS_breaking_pulse_length_scanning/SCS1', doc_format='png')
# find_and_analyse_scs_profiles('mount/14-05-26_repetition_study/SCS1_pplcwr/', doc_format='png')
# Analysis/2026/04-06/11-05-26_SCS_breaking_pulse_length_scanning/mount/11-05-26_SCS_breaking_pulse_length_scanning