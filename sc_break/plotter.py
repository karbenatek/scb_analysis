import matplotlib.pyplot as plt
import os
import gc_utils.info as info
import numpy as np
from sc_break import  SHIM_ORDER, SHIM_CHANNELS, METADATA, SHIM13_ORDER
from sc_break.parser import get_CH_info, set_shimnames

# SHIM13_ORDER = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'M', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1']
# SHIM_ORDER = []
# SHIM_CHANNELS = [[6,5,4,3,2,1,0],[0,1,2,3,6,5]]
# SHIM13_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
#                '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78', '#98df8a']
# plt.get_cmap('tab20')
tab20 = plt.cm.get_cmap('tab20')
SHIM_COLORS = [tab20(19)]
for i in range(6):
    SHIM_COLORS = [tab20(i*2)] + SHIM_COLORS + [tab20(i*2 + 1)]

def plot_hs_signal(time, voltage, label=None, savepath=None):
    """
    Plot Hall Sensor signal.

    Parameters:
    - time: array-like, time data
    - voltage: 2D array-like, voltage data for each pulse sequence
    - cfg: dict, configuration parameters
    - label: str, optional label for the plot
    
    """
    plot_info = info.read().get('plot',{})
    
    fig_signal, ax_signal = plt.subplots()
    
    print(METADATA[0])
    
    ignored_shims = plot_info.get('ignore_shims', [])
    for i in range(len(voltage)):
        if SHIM_ORDER[i] in ignored_shims:
            print(f" Skipping {SHIM_ORDER[i]}")
            continue
        ax_signal.plot(
            time*1e-3,
            voltage[i],
            label=SHIM_ORDER[i],
            color=SHIM_COLORS[i % len(SHIM_COLORS)],
            # marker='.',
        )

    ax_signal.set_title('HS signal' + (f'\n{label}' if label else ''))
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


def subplot_hs_signal(time, voltage, label=None, savepath=None):
    """
    Plot Hall Sensor signal in subplots.

    Parameters:
    - time: array-like, time data
    - voltage: 2D array-like, voltage data for each pulse sequence
    - cfg: dict, configuration parameters
    - label: str, optional label for the plot
    
    """
    plot_info = info.read().get('plot',{})
    
    ignored_shims = plot_info.get('ignore_shims', [])
    indices_to_plot = []
    for i in range(len(voltage)):
        if SHIM_ORDER[i] in ignored_shims:
            print(f" Skipping {SHIM_ORDER[i]}")
            continue
        indices_to_plot.append(i)

    fig_signal, axes = plt.subplots(nrows=len(indices_to_plot), ncols=1, sharex=True, figsize=(6, 28), dpi=150)
    if len(indices_to_plot) == 1:
        axes = [axes]

    for ax, i in zip(axes, indices_to_plot):
        ax.plot(
            time*1e-3,
            voltage[i],
            color=SHIM_COLORS[i % len(SHIM_COLORS)],
        )
        ax.set_ylabel('Voltage (mV)')
        ax.grid()
        ax.text(
            0.02,
            0.98,
            SHIM_ORDER[i],
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    
    axes[-1].set_xlabel('Time (s)')
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)

    fig_signal.suptitle('HS signal' + (f'\n{label}' if label else ''))
    fig_signal.tight_layout(rect=[0, 0, 1, 0.95])

    if plot_info.get('show_cfg', False):
        cfg_text = '\n'.join([f"{key.replace('#','')}: {value}" for key, value in cfg.items()])
        axes[0].text(
            0.02,
            0.98,
            cfg_text,
            transform=axes[0].transAxes,
            fontsize=8,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    if savepath:
        fig_signal.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def sobplot_neighbors_hs_signal(time, voltage, label=None, savepath=None):
    plot_info = info.read().get('plot',{})
    
    i_scs = METADATA[0]['scs']['i']
    
    shims_names = get_shims_and_neigbors_names(i_scs)   
    main_shims, neighbor_shims = shims_names['mains'], shims_names['neighbors']
    main_and_neighbor_shims = main_shims + neighbor_shims

    ignored_shims = plot_info.get('ignore_shims', [])

    for shim in SHIM_ORDER:
        if shim not in main_and_neighbor_shims:
            ignored_shims.append(shim)

    indices_to_plot = []
    for i in range(len(voltage)):
        if SHIM_ORDER[i] in ignored_shims:
            # print(f" Skipping {SHIM_ORDER[i]}")
            continue
        indices_to_plot.append(i)

    fig_signal, axes = plt.subplots(nrows=len(indices_to_plot), ncols=1, sharex=True, figsize=(12, 28), dpi=150)
    if len(indices_to_plot) == 1:
        axes = [axes]

    for ax, i in zip(axes, indices_to_plot):
        ax.plot(
            time*1e-3,
            voltage[i],
            color=SHIM_COLORS[i % len(SHIM_COLORS)],
        )
        ax.set_ylabel('Voltage (mV)')
        ax.grid()
        ax.text(
            0.02,
            0.98,
            SHIM_ORDER[i],
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    
    axes[-1].set_xlabel('Time (s)')
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)

    fig_signal.suptitle('HS signal' + (f'\n{label}' if label else ''))
    fig_signal.tight_layout(rect=[0, 0, 1, 0.95])

    if plot_info.get('show_cfg', False):
        cfg_text = '\n'.join([f"{key.replace('#','')}: {value}" for key, value in cfg.items()])
        axes[0].text(
            0.02,
            0.98,
            cfg_text,
            transform=axes[0].transAxes,
            fontsize=8,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
    if savepath:
        fig_signal.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_pulse_analysis(pulse_analysis, signal = None, label=None, savepath=None):
    plot_info = info.read().get('plot',{})
    
    i_scs = METADATA[0]['scs']['i']
    
    shims_names = get_shims_and_neigbors_names(i_scs)   
    main_shims, neighbor_shims = shims_names['mains'], shims_names['neighbors']
    main_and_neighbor_shims = main_shims + neighbor_shims

    fig, ax = plt.subplots()

    time = pulse_analysis['pulse_time']
    pulse_height = pulse_analysis['pulse_height']

    num_channels = pulse_height.shape[1]
    for i in range(num_channels):
        if SHIM_ORDER[i] in main_and_neighbor_shims:
            ax.plot(
                time*1e-3,
                pulse_height[:,i],
                label=SHIM_ORDER[i],
                color=SHIM_COLORS[i % len(SHIM_COLORS)],
            )
    

    ax.set_title('Pulse Analysis' + (f'\n{label}' if label else ''))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Pulse Height (mV)')

    ax.legend(loc='upper right')
    
    # Additional figure with only used shims
    fig2, (ax2, ax3) = plt.subplots(2, 1, sharex=True)
    for i in range(num_channels):
        if SHIM_ORDER[i] in main_shims:
            ax2.plot(
                time*1e-3,
                pulse_height[:,i],
                label=SHIM_ORDER[i],
                # color=SHIM_COLORS[i % len(SHIM_COLORS)],
                marker='o',
                markersize=4,
            )
            if signal is not None:
                t_signal, v_signal = signal
                ax3.plot(
                    t_signal*1e-3,
                    np.array(v_signal[i, :]) - v_signal[i, 0], 
                    marker='',
                    ls='-',
                    lw=0.5,
                    label=SHIM_ORDER[i],
                    # color=SHIM_COLORS[i % len(SHIM_COLORS)],
                    alpha=0.8,
                )
    ax3.set_ylabel('Signal (mV)')
    
    ax2.set_title('Pulse Analysis (Used Shims Only)' + (f'\n{label}' if label else ''))
    ax3.set_xlabel('Time (s)')
    ax2.set_ylabel('Pulse Height (mV)')
    ax2.legend(loc='upper right')
    # ax3.legend(loc='upper right')
    ax.grid()
    ax2.grid()
    ax3.grid()
    fig.tight_layout()
    fig2.tight_layout()
    
    # Set identical x-axis limits for all subplots
    # if signal is not None:
    #     t_signal, _ = signal
    #     x_min = min(time.min()*1e-3, t_signal.min()*1e-3)
    #     x_max = max(time.max()*1e-3, t_signal.max()*1e-3)
    #     ax.set_xlim(x_min, x_max)
    #     ax2.set_xlim(x_min, x_max)
    #     ax3.set_xlim(x_min, x_max)

    if savepath:
        savepath1 = savepath.replace('_pulse_analysis', '_pulse_analysis_wneighbors')

        fig.savefig(savepath1)
        fig2.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath1)}")
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_all_signleSCS_pulse_analysis(pulse_analysis_data, i_scs=1, label=None, savedir=None):
    ignore_before_t0 = info.read().get('scb_analysis',{}).get('ignore_before_t0', False)

    metadata = METADATA[0]
    get_CH_info(metadata)
    shim_order = set_shimnames(metadata)

    out_doc_format = info.read().get('plot',{}).get('out_doc_format', 'png')
    vpp0 = pulse_analysis_data[0]['Vpp']
    vpp1 = pulse_analysis_data[-1]['Vpp']



    vpp_range = info.read().get('scb_analysis',{}).get('all_pulse_analysis_plot',{}).get('vpp_range', None)
    show_error_bars = info.read().get('scb_analysis',{}).get('all_pulse_analysis_plot',{}).get('show_error_bars', True)

    
    shims_names = get_shims_and_neigbors_names(i_scs)   
    main_shims, neighbor_shims = shims_names['mains'], shims_names['neighbors']
    

    if vpp_range is not None:
        vpp0, vpp1 = vpp_range
        pulse_analysis_data = [d for d in pulse_analysis_data if vpp0 <= d['Vpp'] <= vpp1]
        
    
    fig_main, axs = plt.subplots(len(main_shims), 1, figsize=(12, 2 + 3*len(main_shims)), dpi=150, sharex=True)
    if len(main_shims) == 1:
        axs = [axs]
    for ax, shim in zip(axs, main_shims):
        i_chan = SHIM_ORDER.index(shim)
        for pulse_analysis in pulse_analysis_data:
            if ignore_before_t0:
                valid_indices = pulse_analysis['time'] >= 0
            else:
                valid_indices = np.ones_like(pulse_analysis['time'], dtype=bool)

            time = pulse_analysis['time'][valid_indices]
            pulse_height = pulse_analysis['pulses'][i_chan, valid_indices]
            yerr = pulse_analysis.get('error', [None])[i_chan][valid_indices] if 'error' in pulse_analysis else None

            line, = ax.plot(
                time*1e-3,
                pulse_height,
                label=f'Vpp={pulse_analysis["Vpp"]} V',
            )
            if yerr is not None and show_error_bars:
                ax.errorbar(
                    time*1e-3,
                    pulse_height,
                    yerr=yerr,
                    fmt='none',
                    capsize=3,
                    alpha=0.5,
                    color=line.get_color(),
                )
        if shim == main_shims[0]:
            ax.set_title('Pulse Analysis' + f'\nShim {shim}')
        else:
            ax.set_title(f'Shim {shim}')
            
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Pulse Height (mV)')
        ax.legend(loc='upper right')
        ax.grid()
    
    fig_main.tight_layout()
    
    if savedir:
        # os.path.join(pulse_analysis_dir, f'_pulse_analysis.{out_doc_format}'
        savepath = os.path.join(savedir, f'SCS={i_scs}_VPP={vpp0}-{vpp1}_pulse_analysis_main.{out_doc_format}')
        fig_main.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()


    # Put everything to one figure
    fig_all, axs = plt.subplots(len(shim_order), 1, figsize=(12, 2 + 3*len(shim_order)), dpi=150, sharex=True)
    for i_chan, shim in enumerate(shim_order):
        ax = axs[i_chan]
        for pulse_analysis in pulse_analysis_data:
            if ignore_before_t0:
                valid_indices = pulse_analysis['time'] >= 0
            else:
                valid_indices = np.ones_like(pulse_analysis['time'], dtype=bool)

            time = pulse_analysis['time'][valid_indices]
            pulse_height = pulse_analysis['pulses'][i_chan, valid_indices]
            yerr = pulse_analysis.get('error', [None])[i_chan][valid_indices] if 'error' in pulse_analysis else None

            line, = ax.plot(
                time*1e-3,
                pulse_height,
                label=f'Vpp={pulse_analysis["Vpp"]} V',
            )
            if yerr is not None and show_error_bars:
                ax.errorbar(
                    time*1e-3,
                    pulse_height,
                    yerr=yerr,
                    fmt='none',
                    capsize=3,
                    alpha=0.5,
                    color=line.get_color(),
                )
        if shim == shim_order[-1]: ax.set_xlabel('Time (s)')

        ax.set_title(f'Shim {shim}')
        ax.set_ylabel('Pulse Height (mV)')
        ax.legend(loc='upper right')
        ax.grid()
    fig_all.tight_layout()
    if savepath:
        savepath = os.path.join(savedir, f'SCS={i_scs}_VPP={vpp0}-{vpp1}_pulse_analysis_all.{out_doc_format}')

        fig_all.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def get_shims_and_neigbors_names(i_scs, n_shims=13):
    """
    Get list of shims to plot based on the main SCS index.
    
    Parameters:
    - i_scs: int, index of the main SCS (1-indexed)
    - n_shims: int, total number of shims (default 13)
    
    Returns:
    - dict: {'mains': {'names': list of main shim names},
             'neighbors': {'names': list of neighbor shim names}}
    """
    

    middle_idx = n_shims // 2 + 1
    if n_shims % 2 == 0: # even number of shims call parameter error 
        raise ValueError("n_shims must be an odd number.")
    
    main_shims = [f'R{i_scs}', f'L{i_scs}'] 

    if i_scs == middle_idx:  # Main shim is middle
        neighbors = [f'R{middle_idx}', f'L{middle_idx}']
        main_shims = ['M']
    elif i_scs == 1:
        neighbors = [f'R2', f'L2',]
    elif i_scs == int(n_shims/2): # Main shim is next to middle
        neighbors = [f'R{middle_idx-2}', 'M', f'L{middle_idx-2}']
    else:
        neighbors = [f'R{i_scs-1}', f'R{i_scs+1}', f'L{i_scs+1}', f'L{i_scs-1}']
    
    return {'mains': main_shims, 'neighbors': neighbors}



def plot_pulse_edge_analysis(pulse_edge_analysis, label=None, savepath=None):    
    i_scs = METADATA[0]['scs']['i']
    # print(pulse_edge_analysis['voltage_chunks'][0])
    n_ch = len(pulse_edge_analysis['voltage_chunks'][0][0])
    print(n_ch)
    fig, axs = plt.subplots(n_ch ,1, sharex=True, figsize=(8, 4*n_ch), dpi=150)

    time_chunks = pulse_edge_analysis['time_chunks']
    voltage_chunks = pulse_edge_analysis['voltage_chunks']

    for i in range(n_ch):
        for j, time in enumerate(time_chunks):    
            voltage = voltage_chunks[j][:,i]
            axs[i].plot(
                time[:]*1e-3,
                voltage,
                alpha=0.7,
                # label=SHIM_ORDER[i],
                # color=SHIM_COLORS[i % len(SHIM_COLORS)],
            )
            axs[i].set_ylabel(f'Voltage (ms)')
            axs[i].grid()
            axs[i].text(
                0.02,
                0.98,
                SHIM_ORDER[i],
                transform=axs[i].transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
            )
        if i < n_ch - 2:
            axs[i].set_xticklabels([])

    axs[0].set_title('Pulse Edge Analysis' + (f'\n{label}' if label else ''))
    axs[-1].set_xlabel('Time (s)')
    # axs[-1].legend(loc='upper right')
    fig.tight_layout()
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()
