from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_scba_indir, analyse_scba, find_and_analyse_scs_profiles

# analyse_scba_indir('mount/data/')
# analyse_scba('mount/SCS1/HS_reading_time=11-05-26_18-40-50.csv')
find_and_analyse_scs_profiles('mount/SCS1/', doc_format='png')
