import sys, os, __main__

# add gc_utils
import gc_utils.remote as remote
# mount data as specified in local info.toml
remote.mount_data()

this_dir = os.path.dirname(os.path.abspath(__main__.__file__))
os.chdir(this_dir) # set working directory to script directory