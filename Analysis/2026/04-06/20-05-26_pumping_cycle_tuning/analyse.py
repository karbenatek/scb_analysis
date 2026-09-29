from utils import *
import gc_utils.info as info
from sc_break.analysis import find_and_analyse_scs_profiles, analyse_scs_profile

# analyse_scba_indir('mount/data/')
# analyse_scba('mount/SCS1/HS_reading_time=11-05-26_18-40-50.csv')
# find_and_analyse_scs_profiles('mount/', doc_format='png')
# find_and_analyse_scs_profiles('mount/SCS1_plswr/', doc_format='png')

# for i in  range(3, 4):
    # find_and_analyse_scs_profiles(f'mount/tuning0{i}', doc_format='png')
find_and_analyse_scs_profiles('mount/', doc_format='png')
# analyse_scs_profile('mount/scan3/HS_reading_time=21-05-26_15-54-00.csv', doc_format='png')
