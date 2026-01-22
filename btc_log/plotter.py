import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from btc_log.parser import load_log

def plot_temp(logfilepath, t_min="", t_max="", to_plot=['Cold-head temp (K)'], savepath=None):
    """
    Plot temperature data over time.

    Parameters:
    - time: array-like, time data
    - temperatures: dict, keys are labels and values are temperature data arrays
    - t_min: float, minimum temperature for y-axis
    - t_max: float, maximum temperature for y-axis
    - savepath: str, optional path to save the plot
    """
    log = load_log(logfilepath)
    time = log['Timestamp']
    temperatures = {label: log[label] for label in to_plot}
    fig, ax = plt.subplots(figsize=(10, 6))

    for label, temp_data in temperatures.items():
        ax.plot(time, temp_data, label=label.split(' temp')[0])

    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature [K]')

    # set x limits
    t_min = pd.to_datetime(t_min, dayfirst=True) if t_min else time[0]
    t_max = pd.to_datetime(t_max, dayfirst=True) if t_max else time[-1] 
    ax.set_xlim(t_min, t_max)

    # Format x-axis for dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    fig.autofmt_xdate()

    # Add grid and legend
    ax.grid()
    ax.legend()
    fig.tight_layout()

    if savepath:
        plt.savefig(savepath)
        print(f"Plot saved to {savepath}")
    else:
        plt.show()

    return fig, ax