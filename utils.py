import sys, os, __main__

sys.path.append('../') # to import from parent directory
# add gc_utils
import gc_utils.remote as remote
# mount data as specified in local info.toml
remote.mount_data()

# set font and figure size for plotting
from gc_utils.pyplot import *
set_font_and_fig()


this_dir = os.path.dirname(os.path.abspath(__main__.__file__))
os.chdir(this_dir) # set working directory to script directory