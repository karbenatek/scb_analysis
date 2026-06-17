from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_scba, analyse_scba_indir
from sc_break.plotter import SHIM13_ORDER

analyse_scba_indir('data/',"pdf")
# analyse_scba('data/HS_reading_time=14-01-26_17-05-33.csv')