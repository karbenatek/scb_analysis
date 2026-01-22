import matplotlib.pyplot as plt
import os
import gc_utils.info as info
import numpy as np

SHIM13_ORDER = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'M', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1']
# SHIM13_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
#                '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78', '#98df8a']
# plt.get_cmap('tab20')
tab20 = plt.cm.get_cmap('tab20')
SHIM13_COLORS = [tab20(19)]
for i in range(6):
    SHIM13_COLORS = [tab20(i*2)] + SHIM13_COLORS + [tab20(i*2 + 1)]
def plot_hcl_pulses_signal(time, voltage, cfg, label=None, intervals=[], savepath=None):
    """
    Plot HCL pulse sequences.

    Parameters:
    - time: array-like, time data
    - voltage: 2D array-like, voltage data for each pulse sequence
    - cfg: dict, configuration parameters
    - label: str, optional label for the plot
    
    """
    plot_info = info.read().get('plot',{})
    
    
    fig_signal, ax_signal = plt.subplots()

    if intervals:
        for interval in intervals:
            down_start, down_end, rising_edge, high_start, high_end, falling_edge = interval
            
            # Example spans (only the active one kept)
            ax_signal.axvspan(high_start*1e-3, high_end*1e-3, color='blue', alpha=0.2)

    n_pulses = voltage.shape[0]
    
    ignored_shims = plot_info.get('ignore_shims', [])
    for i in range(n_pulses):
        if SHIM13_ORDER[i] in ignored_shims:
            print(f" Skipping {SHIM13_ORDER[i]}")
            continue
        ax_signal.plot(
            time*1e-3,
            voltage[i],
            label=SHIM13_ORDER[i],
            color=SHIM13_COLORS[i % len(SHIM13_COLORS)],
            marker='.',
        )

    ax_signal.set_title('HCL Pulse Sequence' + (f' - {label}' if label else ''))
    ax_signal.set_xlabel('Time (s)')
    ax_signal.set_ylabel('Voltage (mV)')

    # Add legend, grid, layout
    ax_signal.legend(loc='upper right')
    ax_signal.grid()
    fig_signal.tight_layout()


    if plot_info.get('show_cfg', False):
        # Create config text
        cfg_text = '\n'.join([f"{key.replace('#','')}: {value}" for key, value in cfg.items()])
        # Place text box in upper left
        ax_signal.text(
            0.02,
            0.98,
            cfg_text,
            transform=ax_signal.transAxes,
            fontsize=8,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    

    # Saving or showing
    if savepath:
        fig_signal.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()


def plot_hcl_pulses(sequence, pulse_heights, pulse_errors, cfg, label=None, savepath=None):
    
    """
    Plot HCL pulse heights.

    Parameters:
    - pulse_heights: array-like, heights of each pulse
    - sequence: array-like, pulse sequence values
    - cfg: dict, configuration parameters
    - label: str, optional label for the plot
    
    """
    plot_info = info.read().get('plot',{})
    
    
    fig_pulses, ax_pulses = plt.subplots()

    n_channels = pulse_heights.shape[0]
    n_points   = len(sequence)

    # Horizontal jitter so points don't overlap
    # Example: for 3 channels → [-0.1, 0, +0.1]
    jitter = np.linspace(-0.35, 0.35, n_channels)
    ignored_shims = plot_info.get('ignore_shims', [])
    
    # Plot each channel
    for i, (pulses,error) in enumerate(zip(pulse_heights, pulse_errors)):
        if SHIM13_ORDER[i] in ignored_shims:
            print(f" Skipping {SHIM13_ORDER[i]}")
            continue
        # X positions with jitter
        x = np.arange(n_points) + jitter[i]

        # Error bars (replace 1 with your array later)
        ax_pulses.errorbar(
            x,
            pulses,
            yerr=error,                          # placeholder, change later
            fmt='o-',                           # line + circle markers
            color=SHIM13_COLORS[i % len(SHIM13_COLORS)],
            capsize=4,                          # small caps on error bars
            label=SHIM13_ORDER[i]
        )

    # Vertical separators between regions
    for x in range(1, n_points):
        ax_pulses.axvline(x - 0.5, color="gray", linestyle="--", alpha=0.3)
    ax_pulses.set_xlim(-0.5, n_points)
    # X ticks & labels
    ax_pulses.set_xticks(range(n_points))
    ax_pulses.set_xticklabels([f"{cur:.1f} A" for cur in sequence])

    # Labels & title
    ax_pulses.set_title('HCL Pulse Heights' + (f' - {label}' if label else ''))
    ax_pulses.set_xlabel('Pulse amplitude')
    ax_pulses.set_ylabel('Pulse Height (mV)')

    ax_pulses.grid(alpha=0.3)
    ax_pulses.legend()


    # Add grid, layout
    ax_pulses.grid(axis='y')
    fig_pulses.tight_layout()


    if plot_info.get('show_cfg'):
        # Create config text
        cfg_text = '\n'.join([f"{key.replace('#','')}: {value}" for key, value in cfg.items()])
        # Place text box in upper left
        ax_pulses.text(
            0.02,
            0.98,
            cfg_text,
            transform=ax_pulses.transAxes,
            fontsize=8,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    

    # Saving or showing
    if savepath:
        fig_pulses.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()
    