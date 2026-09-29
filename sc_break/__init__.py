import sys
import numpy as np
import gc_utils.info as info

from sc_break.routine_fun import *

SHIM13_ORDER = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'M7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1']
SHIM_ORDER = []
SHIM_CHANNELS = [[6,5,4,3,2,1,0],[0,1,2,3,6,4]]
METADATA = [None]
DOC_FORMATS = ['png','pdf']


# class Shim:
#     def __init__(self, name = None, channel = None, i_ch = None):
#         self.name = name
#         self.channel = channel
#         self.i_ch = i_ch

