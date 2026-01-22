import matplotlib.pyplot as plt
import os
import gc_utils.info as info
import numpy as np
from current_rampup.parser import *


def plot_RI_characteristic(I, R, metadata, savepath=None):
    """
    Plot Resistance vs Current characteristic.

    Parameters:
    - I: array-like, current data
    - R: array-like, resistance data
    - metadata: dict, metadata information
    - label: str, optional label for the plot
    - savepath: str, optional path to save the plot
    """
    
    fig_RI, ax_RI = plt.subplots()

    ax_RI.plot(I, R, marker='o', linestyle='-')
    if 'T' in metadata.keys():
        ax_RI.set_title(f'Resistance vs Current at T={metadata["T"]}')
    else:
        ax_RI.set_title('Resistance vs Current')
        
    
    ax_RI.set_xlabel('Current (A)')
    ax_RI.set_ylabel('Resistance (ohm)')

    # Add grid, layout
    ax_RI.grid()
    fig_RI.tight_layout()

    if savepath:
        os.makedirs(os.path.dirname(savepath), exist_ok=True)
        fig_RI.savefig(savepath)
        print(f"Plot saved to {savepath}")

    return fig_RI, ax_RI

def plot_RI_indir(dirpath):
    """
    Plot Resistance vs Current characteristic for all files in a directory.

    Parameters:
    - dirpath: str, path to the directory containing data files
    """
    plt.figure(figsize=(10,6))

    for filename in os.listdir(dirpath):
        if filename.endswith('.csv') and filename.startswith('HCL-RxI_'):
            filepath = os.path.join(dirpath, filename)
            I, R, metadata = get_RIchar(filepath)
            plt.plot(I, R, marker='o', linestyle='-', label=f"{metadata.get('T','unknown')}")

    plt.title('Resistance vs Current for all measurements')
    plt.xlabel('Current (A)')
    plt.ylabel('Resistance (ohm)')
    plt.grid()

    # --- shrink plot width ---
    fig = plt.gcf()
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0 -0.05, box.y0, box.width * 0.85, box.height])

    # --- legend ---
    plt.legend(title='Target cold-head temperature',
            bbox_to_anchor=(1.05, 1),
            loc='upper left')
    # plt.tight_layout()
    savepath = os.path.join(dirpath, 'RxI_all.png')
    plt.savefig(savepath, dpi=300)
    print(f"Plot saved to {savepath}")
    # plt.show()

def plot_RI_signal(RxI_signal_data: RxI_signal_ParsedData, savepath=None):
    """
    Plot Resistance vs Time signal for a given current.

    Parameters:
    - I: array-like, current data
    - R: array-like, resistance data
    - time_s: array-like, time data in seconds
    - current_A: float, current value for the measurement
    - savepath: str, optional path to save the plot
    """
    fig, ax = plt.subplots()
    for block in RxI_signal_data.measurements:
        ax.plot(block.time_s, block.resistance_ohm, linestyle='-', label=f'I={block.current_A} A')
        
    ax.set_title(f'Resistance vs Time at T={RxI_signal_data.metadata['T']}K')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Resistance (ohm)')
    ax.grid()
    ax.legend(bbox_to_anchor=(1.05, 1),
            loc='upper left')
    box = ax.get_position()
    
    ax.set_position([box.x0 -0.05, box.y0, box.width * 0.85, box.height])
    if savepath:
        os.makedirs(os.path.dirname(savepath), exist_ok=True)
        fig.savefig(savepath)
        print(f"Plot saved to {savepath}")
    else:
        plt.show()

def plot_RI_signal_indir(dirpath):
    """
    Plot Resistance vs Time signal for all files in a directory.

    Parameters:
    - dirpath: str, path to the directory containing data files
    """
    plt.figure(figsize=(10,6))
    for filename in os.listdir(dirpath):
        if filename.endswith('.csv') and filename.startswith('HCL-RxI-signal_'):
            filepath = os.path.join(dirpath, filename)
            parsed_data = get_RI_signal(filepath)
            T = parsed_data.metadata.get('T', 'unknown')
            I0 = parsed_data.measurements[0].current_A
            I1 = parsed_data.measurements[-1].current_A
            plot_RI_signal(parsed_data, savepath= dirpath + f'/RxI-signal_{T}K_({I0:.2f}-{I1:.2f})A.png')
