from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_hcl_current_effect_on_pumping, analyse_flux_pumping_stages_indir, find_and_analyse_scs_profiles, analyse_stages_indir, analyse_stages


# analyse_stages_indir('mount/redo17/test3', walk=0)
analyse_hcl_current_effect_on_pumping('mount/redo17')
# analyse_hcl_current_effect_on_pumping('mount/GOOD-redo17')
# analyse_stages_indir('mount/redo13', walk= False)
# analyse_stages_indir('mount/redo10')
# analyse_hcl_current_effect_on_pumping('mount/redo8')
# analyse_stages('mount/redo7/HS_reading_time=17-06-26_13-05-11.csv')
# analyse_stages('mount/redo6/tuning/HS_reading_time=16-06-26_15-50-53.csv')Analysis/2026/04-06/11-06-26_pumping_current_scan/mount/redo7/HS_reading_time=17-06-26_10-52-28.csv