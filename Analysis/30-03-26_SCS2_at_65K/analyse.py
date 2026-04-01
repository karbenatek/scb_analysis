from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_scba_indir, analyse_scba

# analyse_scba_indir('mount/data/')
analyse_scba('mount/data/HS_reading_time=30-03-26_20-12-11.csv')
plt.show()