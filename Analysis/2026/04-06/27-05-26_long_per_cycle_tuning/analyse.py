from utils import *

import gc_utils.info as info
from sc_break.analysis import find_and_analyse_scs_profiles, analyse_scs_profile

find_and_analyse_scs_profiles('mount/50s/pumping', doc_format='png')