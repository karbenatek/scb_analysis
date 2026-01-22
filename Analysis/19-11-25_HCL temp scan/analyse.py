from utils import *
# from hcl_pulse.parser import parse_config_string, get_hcl_pulse_data
import gc_utils.info as info
import btc_log.parser as btc_log
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

data = btc_log.load_log('data/13-11-25_SC-trans-scan.csv')

samples = [pd.to_datetime(t, dayfirst=True) for t in 
    [
    "13/11/2025 15:05:00",
    "13/11/2025 17:05:00",
    "13/11/2025 19:05:00",
    "13/11/2025 21:05:00",
    "13/11/2025 23:05:00",
    
    "14/11/2025 01:05:00",
    "14/11/2025 03:05:00",
    "14/11/2025 05:05:00",
    "14/11/2025 10:20:00",
    "14/11/2025 12:20:00",
    "14/11/2025 14:20:00",
    "14/11/2025 17:02:00",
    "14/11/2025 19:02:00",
    "15/11/2025 00:00:00",
    ]
    
]
# get resistances at sample times, note that data has columns in numpy arrays
samp_res = []
samp_chtemp = []
samp_4wtemp = []
for sample in samples:
    # find closest timestamp in data
    idx = (np.abs(data['Timestamp'] - sample)).argmin()
    samp_res.append(data['DMM1 2W Resistance (ohm)'][idx])
    samp_chtemp.append(data['Cold-head temp (K)'][idx])
    samp_4wtemp.append(data['4way cross temperature (K)'][idx])


fig, (ax_temp, ax_res) = plt.subplots(2,1,figsize=(10, 6), sharex=True)
fig.suptitle('HCL temperature scan')

ax_temp.plot(data['Timestamp'], data['Cold-head temp (K)'], label='Cold-head')
ax_temp.plot(data['Timestamp'], data['4way cross temperature (K)'], label='4-way cross')
ax_temp.plot([],color='green', linestyle='--', alpha=0.5, label='Sample times')
for sample in samples:
    ax_temp.axvline(sample, color='green', linestyle='--', alpha=0.5)
    ax_res.axvline(sample, color='green', linestyle='--', alpha=0.5)
# add legend for axvline




ax_temp.legend()

ax_res.plot(data['Timestamp'], data['DMM1 2W Resistance (ohm)'], color='orange')

ax_res.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M:%S"))
ax_res.xaxis.set_major_locator(mdates.AutoDateLocator())

xmin = pd.to_datetime("13/11/2025 13:01:15", dayfirst=True)
xmax = pd.to_datetime("15/11/2025 06:00:00", dayfirst=True)
ax_temp.set_xlim([xmin, xmax])
ax_res.set_xlim([xmin, xmax])

ax_res.set_xlabel('Time')
ax_res.set_ylabel('HCL resistance [Ohm]')
ax_temp.set_ylabel('Temperature [K]')
# pass ax_res ticks to ax_temp
ax_temp.set_yticks(ax_temp.get_yticks())



#set grid
ax_temp.grid(True)
ax_res.grid(True)
# ax_temp.set_xticks([])


plt.tight_layout()
plt.gcf().autofmt_xdate()  # auto-rotate labels


fig2, ax = plt.subplots(figsize=(6,4))

fig2.suptitle('HCL resistance vs temperature after thermalisation')
ax.plot(samp_chtemp, samp_res, 'o-', label='Resistance vs Cold-head temp')
ax.plot(samp_4wtemp, samp_res, 'o-', label='Resistance vs 4-way cross temp')
ax.set_xlabel('Temperature [K]')
ax.set_ylabel('HCL resistance [Ohm]')
ax.legend()
fig2.tight_layout()

fig.savefig('data/HCL_temp_scan.png', dpi=300)
fig2.savefig('data/HCL_res_vs_temp.png', dpi=300)

# plt.show()