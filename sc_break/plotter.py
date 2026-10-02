import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import scb_analysis
# import sc_break
import numpy as np
from sc_break import *
from sc_break.parser import get_CH_info, set_shimnames
from sc_break.routine_fun import get_SCS_profile_rising_edge_times, get_SCS_profile_period, get_SCS_profile_all_edges_times
from sc_break import DOC_FORMATS
import gc_utils.info as info

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

# subplot function with some default parameters
def subplots(*args, **kwargs):
    kwargs.setdefault("num", 1)
    kwargs.setdefault("clear", True)
    return plt.subplots(*args, **kwargs)



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
    
    fig_signal, ax_signal = subplots(num = 1, clear=True)
    
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


def subplot_hs_signal(time, voltage, label=None, savepath=None, dpi=150):
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
    for i in range(voltage.shape[1]):
        if SHIM_ORDER[i] in ignored_shims:
            print(f" Skipping {SHIM_ORDER[i]}")
            continue
        indices_to_plot.append(i)
    fig_width = 12
    fig_signal, axes = subplots(
        nrows=len(indices_to_plot), 
        ncols=1, sharex=True, 
        figsize=(fig_width, fig_width*3/4)  ,
        dpi=dpi,
        )
    if len(indices_to_plot) == 1:
        axes = [axes]
    axes[-1].set_xlim([0, int(time[-1]/1000)])
    for ax, i in zip(axes, indices_to_plot):
        ax.plot(
            time*1e-3,
            voltage[:,i],
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
    fig_signal.tight_layout()
    # fig_signal.tight_layout(rect=[0, 0, 1, 0.95])

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
    
    i_scs = METADATA[0].get('scs', {}).get('i', 0)
    
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

    fig_signal, axes = subplots(nrows=len(indices_to_plot), ncols=1, sharex=True, figsize=(12, 28), dpi=150)
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
def get_pulse_analysis_fig(pulse_analysis, shims_to_plot, label=None):
    fig, ax = subplots()

    time = pulse_analysis['pulse_time']
    pulse_height = pulse_analysis['pulse_height']

    num_channels = pulse_height.shape[1]
    for i in range(num_channels):
        if SHIM_ORDER[i] in shims_to_plot:
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
    ax.grid()
    fig.tight_layout()
    
    return fig

def plot_pulse_analysis(pulse_analysis, signal = None, label=None, savepath=None):
    plot_info = info.read().get('plot',{})
    
    i_scs = METADATA[0].get('scs', {}).get('i', 0)
    shims_names = get_shims_and_neigbors_names(i_scs)   
    main_shims, neighbor_shims = shims_names['mains'], shims_names['neighbors']
    main_and_neighbor_shims = main_shims + neighbor_shims
    # plot all shims if i_scs is not specified (0), otherwise only main and neighbor shims
    shims_to_plot = SHIM_ORDER if i_scs == 0 else main_and_neighbor_shims
    fig, ax = subplots()

    time = pulse_analysis['pulse_time']
    pulse_height = pulse_analysis['pulse_height']

    num_channels = pulse_height.shape[1]
    for i in range(num_channels):
        if SHIM_ORDER[i] in shims_to_plot:
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
    ax.grid()
    fig.tight_layout()
    
    # stop here if i_scs is not specified
    if i_scs == 0:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
        return
    # Additional figure with only used shims
    fig2, (ax2, ax3) = subplots(2, 1, sharex=True)
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
    ax2.grid()
    ax3.grid()
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
        print(f"Plot saved to {os.path.abspath(savepath1)}")
        fig2.savefig(savepath)
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
        
    
    fig_main, axs = subplots(len(main_shims), 1, figsize=(10,1 + 3*len(main_shims)), dpi=150, sharex=True)
    fig_main.subplots_adjust(right=0.85)

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
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1))
        else:
            ax.set_title(f'Shim {shim}')
            
        ax.set_ylabel('Pulse Height (mV)')
        ax.grid()
    ax.set_xlabel('Time (s)')
    
    # fig_main.tight_layout()
    
    if savedir:
        # os.path.join(pulse_analysis_dir, f'_pulse_analysis.{out_doc_format}'
        savepath = os.path.join(savedir, f'SCS={i_scs}_VPP={vpp0}-{vpp1}_pulse_analysis_main.{out_doc_format}')
        fig_main.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()


    # Put everything to one figure
    fig_all, axs = subplots(len(shim_order), 1, figsize=(10, 3*len(shim_order)), dpi=150, sharex=True)
    fig_all.subplots_adjust(right=0.85)
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

        ax.set_title(f'Shim {shim}')
        ax.set_ylabel('Pulse Height (mV)')
        if i_chan == 0: ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1))
        ax.grid()
    ax.set_xlabel('Time (s)')
    
    # fig_all.tight_layout()
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
    i_scs = METADATA[0].get('scs', {}).get('i', 0)
    # print(pulse_edge_analysis['voltage_chunks'][0])
    n_ch = len(pulse_edge_analysis['voltage_chunks'][0][0])
    print(n_ch)
    fig, axs = subplots(n_ch ,1, sharex=True, figsize=(8, 4*(n_ch)), dpi=150)

    time_chunks = pulse_edge_analysis['time_chunks']
    voltage_chunks = pulse_edge_analysis['voltage_chunks']

    for i in range(n_ch):
        for j, time in enumerate(time_chunks):    
            voltage = voltage_chunks[j][:,i]
            axs[i].plot(
                time[:]*1e-3,
                voltage,
                "o-",
                markersize=1,
                alpha=0.7,
                # label=SHIM_ORDER[i],
                # color=SHIM_COLORS[i % len(SHIM_COLORS)],
            )
            axs[i].set_ylabel(f'Voltage (ms)')
            axs[i].grid()
            # Add shim name as text in the upper left corner of each subplot
            axs[i].text(
                0.02,
                0.98,
                SHIM_ORDER[i],
                transform=axs[i].transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
            )
        # if i < n_ch - 3:
        # axs[i].set_xticklabels([])

    axs[0].set_title('Pulse Edge Analysis' + (f'\n{label}' if label else ''))
    axs[-1].set_xlabel('Time (s)')
    # axs[-1].legend(loc='upper right')
    # fig.tight_layout()
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_SCS_profiles(SCS_profiles, label=None, savepath=None):
    fig, ax = subplots()
    for name, profile in SCS_profiles.items():
        time = [0] + profile[:, 0].tolist()
        profile = [0] + profile[:, 1].tolist()
        ax.step(time, profile, label=str(name), where='post')
    ax.set_title('SCS Profiles' + (f'\n{label}' if label else ''))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Duty-cycle (\\%)')
    ax.legend()
    ax.grid()
    fig.tight_layout()
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_SCS_profile_pulse_analysis(pulse_analysis, signal = None, label=None, savepath=None):
    SCS_profiles = METADATA[0].get('SCS_profiles', {})
    if not SCS_profiles:
        print("No SCS profiles found in metadata. Cannot plot SCS profile pulse analysis.")
        return
    
    fig, ax = subplots()

    time = pulse_analysis['pulse_time']
    pulse_height = pulse_analysis['pulse_height']

    num_channels = pulse_height.shape[1]
    for i in range(num_channels):
        ax.plot(
            time*1e-3,
            pulse_height[:,i],
            label=SHIM_ORDER[i],
            color=SHIM_COLORS[i % len(SHIM_COLORS)],
        )
    
    # Overlay SCS profiles
    for name, profile in SCS_profiles.items():
        time_profile = [0] + profile[:, 0].tolist()
        profile_values = [0] + profile[:, 1].tolist()
        ax.step(time_profile, np.array(profile_values)*np.max(pulse_height), label=f'SCS {name}', where='post', linestyle='--')

    ax.set_title('Pulse Analysis with SCS Profiles' + (f'\n{label}' if label else ''))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Pulse Height (mV)')
    ax.legend(loc='upper right')
    ax.grid()
    fig.tight_layout()
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_pulse_sanity(time, voltage, pulse_analysis, pulse_sanity_analysis, savepath=None):
    voltage = np.asarray(voltage)
    if voltage.shape[0] != time.shape[0]:
        if voltage.shape[1] == time.shape[0]:
            voltage = voltage.T
        else:
            raise ValueError("voltage's time dimension must match the length of time (either axis 0 or 1)")

    n_bins = info.read().get('scb_analysis',{}).get('pulse_sanity_analysis',{}).get('n_bins', 60)
    n_ch = voltage.shape[1]
    time_chunks = pulse_sanity_analysis['time_chunks']
    voltage_chunks = pulse_sanity_analysis['voltage_chunks']
    idle_mask_chunks = pulse_sanity_analysis['idle_mask_chunks']
    pulse_mask_chunks = pulse_sanity_analysis['pulse_mask_chunks']
    pedestal_fit_chunks = pulse_sanity_analysis['pedestal_fit_chunks']
    # TODO: figure out hist for pulse/idle, add SCS label to subplots, add lines for margins, add legend
    fig, ax = subplots(n_ch, 3, sharex=False, figsize=(15, 4*n_ch), dpi=150)
    for i_ch in range(n_ch):
        for t,v,p_m,i_m,fit in zip(time_chunks, voltage_chunks, pulse_mask_chunks, idle_mask_chunks, pedestal_fit_chunks):
            ax[i_ch, 0].plot(t*1e-3, fit[:,i_ch],  "--", linewidth=1, alpha=0.4)
            ax[i_ch, 0].plot(t*1e-3, v[:,i_ch],  markersize=3, alpha=0.5)
            ax[i_ch, 0].plot(t[i_m]*1e-3, v[i_m,i_ch],  "x", markersize=2, alpha=0.7)
            ax[i_ch, 0].plot(t[p_m]*1e-3, v[p_m,i_ch],  "o", markersize=3, alpha=0.7)
        ax[i_ch, 0].text(
            0.02,
            0.98,
            SHIM_ORDER[i_ch],
            transform=ax[i_ch, 0].transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )
        # plt.hist(voltage[:,0], bins=n_bins, alpha=0.5, label='All data')
        # plt.hist(voltage[pulse_analysis['idle_mask'],0], bins=n_bins, alpha=0.5, label='Idle data')
        # plt.hist(voltage[i_ch, pulse_analysis['pulse_mask']], bins=n_bins, alpha=0.5, label='Pulse data')
        ax[i_ch, 1].hist(voltage[:,i_ch], bins=n_bins, alpha=0.5, label='All data')
        ax[i_ch, 1].hist(voltage[pulse_analysis['idle_mask'], i_ch], bins=n_bins, alpha=0.5, label='Idle data')
        ax[i_ch, 1].hist(voltage[pulse_analysis['pulse_mask'],i_ch], bins=n_bins, alpha=0.5, label='Pulse data')
        # ax[i_ch, 1].set_title(f'Voltage Distribution - Channel {SHIM_ORDER[i_ch]}')
        ax[i_ch, 1].set_xlabel('Voltage (mV)')
        ax[i_ch, 1].set_ylabel('Count')
    ax[0, 1].legend()

    fig.tight_layout()
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_SCS_profile_sliced(time: np.ndarray, voltage: np.ndarray, SCS_profiles: dict, slice_type: str = 'all_edges', savepath=None):
    
    if slice_type == 'rising_edge':
        slice_points = get_SCS_profile_rising_edge_times(SCS_profiles)
    elif slice_type == 'falling_edge':
        slice_points = get_SCS_profile_falling_edge_times(SCS_profiles)
    elif slice_type == 'all_edges':
        slice_points = get_SCS_profile_all_edges_times(SCS_profiles)
    
    # SCS_profile_period = get_SCS_profile_period(SCS_profiles)
    # if time[-1] / SCS_profile_period > 1.2:
    #     # split arrays into chunks as the SCS profiles repeat
    #     time, voltage = split_arrays_by_period(time, SCS_profile_period, voltage)
    for j, (name, edge) in enumerate(slice_points.items()):
        i_scs = int(name[3:])
        for i_ch, shim in enumerate(SHIM_ORDER):
            if int(shim[1:]) == i_scs:
                break

        re_time = list(np.array(edge)[:,0]*1e3)
        fig, ax = subplots(len(re_time), 1, sharex=False, figsize=(10, 3*len(re_time)), dpi=150)
        if len(re_time) == 1:
            ax = [ax]
        last_profile_value = 0
        for i in range(len(re_time)):
            interval = (re_time[i], re_time[i+1] if i+1 < len(re_time) else time[-1])
            
            mask = (time >= interval[0]) & (time < interval[1])

            # get profile point in the interval
            profile_time = SCS_profiles['norm'][name][:,0]*1e3
            profile_value = SCS_profiles['norm'][name][:,1]
            profile_mask = (profile_time >= interval[0]) & (profile_time < interval[1])
            profile_time -= re_time[i]  # align profile time to rising edge time
            profile_time = np.append(0, profile_time[profile_mask])
            profile_value = np.append(last_profile_value, profile_value[profile_mask])
            if i < len(re_time) - 1:
                profile_time = np.append(profile_time, interval[1] - re_time[i])
                profile_value = np.append(profile_value, profile_value[-1])

            last_profile_value = profile_value[-1]
            

            ax[i].plot(
                time[mask]*1e-3 - re_time[i]*1e-3,
                voltage[mask,i_ch],
                "-",
                markersize=1,
                # alpha=0.7,
                # label=SHIM_ORDER[i],
                # color=SHIM_COLORS[i % len(SHIM_COLORS)],
            )
            ax[i].set_ylabel(f'Voltage (mV)')
            ax[i].grid()
            
            # Create dual axis for profile data
            ax2 = ax[i].twinx()
            ax2.step(
                profile_time*1e-3,
                profile_value,
                where='post',
                label=f'{name} Profile',
                color='red',
                linewidth=2,
                alpha=0.7
            )
            ax2.set_ylabel(f'Duty-cycle (\\%)')

            # add axis tick for profile time points
            ticks = ax[i].get_xticks().tolist()
            ticks += list(profile_time[:-1]*1e-3)
            ticks = sorted(set(ticks))
            ax[i].set_xticks(ticks)
            ax[i].set_xlim(-0.5)
        ax[0].set_title(f'Rising Edge Intervals for {name}')
        ax[-1].set_xlabel('Time (s)')
        fig.tight_layout()
        if savepath:
            filename = os.path.basename(savepath).replace('.png', f'_{slice_type}_{name}.png')
            filepath = os.path.dirname(savepath)
            fig.savefig(os.path.join(filepath, filename))
            print(f"Plot saved to {os.path.abspath(os.path.join(filepath, filename))}")
        else:
            plt.show()

RAW_SIGNAL_PLOT_CFG = {
    'markersize': 1,
    'linewidth': 0.8,
    'alpha': 0.8,
    'linestyle': '-',
}
def shim_sort_key(name):
        if name == 'M':
            numeric_part = 7
        else:
            numeric_part = int(''.join(ch for ch in name if ch.isdigit()))

        prefix_rank = 0 if name.startswith('R') else 1 if name.startswith('L') else 2
        return (numeric_part, prefix_rank)

def plot_SCS_profile_with_repetitions(time: np.ndarray, voltage: np.ndarray, SCS_profiles: dict, pulse_analysis = {}, shims_to_plot = [], savepath=None):
    SCS_profile_period = get_SCS_profile_period(SCS_profiles)
    prep_length = get_PRESCS_profile_length(SCS_profiles)
    time_range = info.read().get('rep_analysis',{}).get('time_range', [])
    


    # split arrays into chunks as the SCS profiles repeat
    prep_time, prep_voltage, time, voltage = chop_preparation(time, prep_length*1e3, voltage)
    time, voltage = split_arrays_by_period(time, SCS_profile_period*1e3, voltage)

    # if time_range:
    #     for i_rep, (_t, _v) in enumerate(zip(time, voltage)):

    #         mask = (_t >= time_range[0]*1e3) & (_t <= time_range[1]*1e3)

    #         time[i_rep] = _t[mask]
    #         voltage[i_rep] = _v[mask]


    x_ticks = []
    shims_to_plot = shims_to_plot if shims_to_plot else SHIM_ORDER
    # order shims based on index, with R-prefixed shims first
    # def shim_sort_key(name):
    #     numeric_part = int(''.join(ch for ch in name if ch.isdigit()))
    #     prefix_rank = 0 if name.startswith('R') else 1 if name.startswith('L') else 2
    #     return (numeric_part, prefix_rank)

    shims_to_plot = sorted(shims_to_plot, key=shim_sort_key)
    for i, shim in enumerate(shims_to_plot):
        if shim[0] == 'M':
            shims_to_plot[i] = 'M7'
    SCS_without_HS_signal = []

    # get profiles that do not have corresponding HS signal in the data
    for SCS in list(SCS_profiles['norm'].keys()):
        SCS_index = SCS[3:]
        if f'L{SCS_index}' not in SHIM_ORDER and f'R{SCS_index}' not in SHIM_ORDER:
            SCS_without_HS_signal.append(SCS)

    # insert SCS_without_HS_signal into Shims_to_plot based on index
    for SCS in SCS_without_HS_signal:
        SCS_index = SCS[3:]
        insert_index = 0
        for i, shim in enumerate(shims_to_plot):
            if int(shim[1:]) > int(SCS_index):
                insert_index = i
                break
            insert_index = i + 1
        shims_to_plot.insert(insert_index, SCS)

    # SCS_with_profile_idx = [int(s[3:]) for s in SCS_profiles['norm'].keys()]

    n_plots =  len(shims_to_plot)

    # RAW SIGNAL PLOTTING
    fig, ax = subplots(n_plots, 1, sharex=True, figsize=(8, 3*n_plots), dpi=150)
    if n_plots == 1: ax = [ax]

    cmap = plt.get_cmap('copper')
        
    n_color = len(time)
    norm = plt.Normalize(vmin=1, vmax=max(n_color-1, 1)+1)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    for i, name in enumerate(shims_to_plot):
        ax[i].text(
            0.02,
            0.98,
            name,
            transform=ax[i].transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )

        if name[0] in ['R', 'L', 'M']:
            i_ch = SHIM_ORDER.index(name)

            for i_color, (t, v) in enumerate(zip(time, voltage)):
                ax[i].plot(
                    t*1e-3,
                    v[:,i_ch],
                    **RAW_SIGNAL_PLOT_CFG,
                    color = cmap(i_color/n_color)
                    # cmap = 'viridis',
                    # label=name,
                    # color=SHIM_COLORS[i % len(SHIM_COLORS)],
                )
            name = f'SCS{int(name[1:])}'
        

        
        ax[i].set_ylabel(f'Voltage (mV)')
        ax[i].grid()
        

        # plot SCS profile
        if name in SCS_profiles['norm'].keys():

            # Create dual axis for profile data
            ax2 = ax[i].twinx()
            for _i,spine in enumerate(ax2.spines.values()):
                if _i in [1]:  # Assuming you want to modify the left and right spines
                    spine.set_edgecolor('red')
            ax2.tick_params(axis='y', colors='red')
            profile_time = SCS_profiles['norm'][name][:,0]*1e3
            profile_time =   np.array([0] + SCS_profiles['norm'][name][:, 0].tolist())
            profile_values = np.array([0] + SCS_profiles['norm'][name][:, 1].tolist())

            ax2.step(profile_time, 
                    np.array(profile_values), 
                    label=f'SCS heating profile' if i == 0 else '',
                    where='post', 
                    color ='red',
                    linewidth=1.6,
                    alpha=0.7,
                    )
            ax2.set_ylabel(f'Duty-cycle (\\%)')
            # ax2.legend(loc='upper right', bbox_to_anchor=(1, 1.15))
        # add axis tick for profile time points
        
        
            pre_name = f'PRE{name}'
            if pre_name in SCS_profiles.get('pre', {}):
                ax[i].plot(
                    prep_time*1e-3 - prep_length,
                    prep_voltage[:,i_ch],
                    "-",
                    # markersize=3,
                    linewidth=1.6,
                    color ='black',
                    label=f'{name} Preparation',
                    # color=SHIM_COLORS[i % len(SHIM_COLORS)],
                )
                prep_profile_time = SCS_profiles['pre'][pre_name][:,0]*1e3
                # prep_profile_value = SCS_profiles['pre'][pre_name][:,1]
                prep_profile_time = np.array([0] + SCS_profiles['pre'][pre_name][:, 0].tolist())
                prep_profile_values = np.array([0] + SCS_profiles['pre'][pre_name][:, 1].tolist())
                ax2.step(prep_profile_time - prep_length, 
                        np.array(prep_profile_values), 
                        label=f'Preparation Profile' if i == 0 else '',
                        where='post', 
                        color ='red',
                        linewidth=1,
                        alpha=0.7,
                        )

                ax[i].legend(loc='upper left', bbox_to_anchor=(0, 1.15))
            x_ticks += ax[i].get_xticks().tolist()
            x_ticks += list(profile_time[:-1])
            # ticks = sorted(set(ticks))

        
    x_ticks = sorted(set(x_ticks + [SCS_profile_period]))
    ax[0].set_title(f'Raw HS reading')
    ax[-1].set_xticks(x_ticks)
    # The axes share x, so this final call controls every subplot.  Do not
    # overwrite the limit requested above when a time range is configured.
    if time_range:
        ax[-1].set_xlim(time_range[0], time_range[1])
    else:
        ax[-1].set_xlim(-prep_length - 0.5, SCS_profile_period + 0.5)
    ax[-1].set_xlabel('Time (s)')
    


    fig.tight_layout()
    fig.subplots_adjust(right=0.9)
    fig.colorbar(
                sm,
                ax=ax,
                orientation='vertical',
                label='Iteration index',
                fraction=0.03,
                pad=0.08,
            )
    # fig.tight_layout()
    
    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()
    
    if not pulse_analysis:
        return
    
    # PULSE ANALYSIS PLOTTING 
    fig, ax = subplots(n_plots, 1, sharex=True, figsize=(10, 3*n_plots), dpi=150)
    if n_plots == 1: ax = [ax]
    
    for i, name in enumerate(shims_to_plot):
        ax[i].text(
                            0.02,
                            0.98,
                            name,
                            transform=ax[i].transAxes,
                            fontsize=9,
                            verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
                        )

        
        if name[0] in ['R', 'L', 'M']:
            i_ch = SHIM_ORDER.index(name)

            pulse_time = pulse_analysis['pulse_time']
            pulse_height = pulse_analysis['pulse_height'][:,i_ch]
            prep_pulse_time, prep_pulse_height, pulse_time, pulse_height = chop_preparation(pulse_time, prep_length*1e3, pulse_height)
            pulse_time, pulse_height = split_arrays_by_period(pulse_time, SCS_profile_period*1e3, pulse_height)

            for i_color, (t, v) in enumerate(zip(pulse_time, pulse_height)):
                ax[i].plot(
                    np.array(t)*1e-3,
                    v,
                    "o-",
                    linewidth=0.7,
                    alpha=0.9,
                    markersize=1.4,
                    color = cmap(i_color/n_color)

                    # label=shim_name,
                    # color=SHIM_COLORS[i_scs % len(SHIM_COLORS)],
                )
            name = f'SCS{int(name[1:])}'

            ax[i].set_ylabel(f'Voltage (mV)')
                
        if name in SCS_profiles['norm'].keys():
            # Overlay SCS profiles
            profile_time = SCS_profiles['norm'][name][:,0]*1e3
            profile_value = SCS_profiles['norm'][name][:,1]
            profile_time =   np.array([0] + SCS_profiles['norm'][name][:, 0].tolist())
            profile_values = np.array([0] + SCS_profiles['norm'][name][:, 1].tolist())
            ax2 = ax[i].twinx()
            ax2.step(profile_time, 
                    np.array(profile_values), 
                    label=f'SCS heating profile' if i == 0 else '',
                    where='post', 
                    color ='red',
                    linewidth=1,
                    alpha=0.7,
                    )

            
            # if i == 0:
            #     ax[i].set_title(f'Pulse Analysis')
            pre_name = f'PRE{name}'
            if pre_name in SCS_profiles.get('pre', {}):
                ax[i].plot(
                    prep_pulse_time*1e-3 - prep_length,
                    prep_pulse_height[:],
                    "o-",
                    # markersize=3,
                    linewidth=1,
                    alpha=0.6,
                    markersize=1.4,
                    color ='red',
                    label=f'{name} Preparation',
                    # color=SHIM_COLORS[i % len(SHIM_COLORS)],
                )
                prep_profile_time = SCS_profiles['pre'][pre_name][:,0]*1e3
                prep_profile_value = SCS_profiles['pre'][pre_name][:,1]
                prep_profile_time =   np.array([0] + SCS_profiles['pre'][pre_name][:, 0].tolist())
                prep_profile_values = np.array([0] + SCS_profiles['pre'][pre_name][:, 1].tolist())
                ax2.step(prep_profile_time - prep_length, 
                        np.array(prep_profile_values),
                        where='post', 
                        color ='red',
                        linewidth=1,
                        alpha=0.7,
                        )
            
            
                ax[i].legend(loc='upper left', bbox_to_anchor=(0, 1.15))
            ax2.set_ylabel('Duty-cycle (\\%)')
            ax2.tick_params(axis='y', colors='red')
            # ax2.legend(loc='upper right', bbox_to_anchor=(1, 1.15))

            for _i,spine in enumerate(ax2.spines.values()):
                if _i in [1]: spine.set_edgecolor('red')
            # fig.show()

        
        ax[i].grid()
    ax[-1].set_xlabel('Time (s)')
    # ticks = ax[i].get_xticks().tolist()
    # ticks += list(profile_time[:-1])
    # ticks = sorted(set(ticks))
    ax[i].set_xticks(x_ticks)
    if time_range:
            ax[0].set_xlim(time_range[0], time_range[1])
    else:
        ax[i].set_xlim(- prep_length - 0.5, SCS_profile_period + 0.5)
    fig.tight_layout()
    fig.subplots_adjust(right=0.9)
    fig.colorbar(
                sm,
                ax=ax,
                orientation='vertical',
                label='Iteration index',
                fraction=0.03,
                pad=0.08,
            )
    
        # input("Press Enter to continue to the next SCS profile...")
    # plot pulse analysis
    if savepath:
        for doc_format in DOC_FORMATS: 
            _savepath = savepath.replace('.'+doc_format, '_pulse_analysis.' + doc_format)
            if _savepath != savepath:
                fig.savefig(_savepath)
                print(f"Plot saved to {os.path.abspath(_savepath)}")
    else:
        plt.show()


def plot_flux_pumping(SCS_stages, savepath=None):
    pumping_stages = [stage for stage in SCS_stages if stage['Name'] == 'fp']
    alignment_stages = [stage for stage in SCS_stages if stage['Name'] == 'flux_alignment']
    flushing_stages = [stage for stage in SCS_stages if stage['Name'] == 'flux_flush']
    idle_stages = [stage for stage in SCS_stages if stage['Name'] == 'idle']

    n_ch = pumping_stages[0]['v'].shape[1]

    
    pumping_plot_cfg = {
        'color': 'red',
        'linewidth': 0.5,
        'linestyle': '-',
        'alpha': 0.9,
    }
    alignment_plot_cfg = {
        'color': 'black',
        'linewidth': 0.5,
        'linestyle': '-',
        # 'alpha': 0.9,
    }
    flushing_plot_cfg = {
        'color': 'orange',
        'linewidth': 0.5,
        'linestyle': '-',
    }
    aligned_plot_cfg = {
        'color': 'green',
        'linewidth': 0.5,
        'linestyle': '',
        'marker': 'o',
        'markersize': 2,
        'capsize':4,
    }
    flushed_plot_cfg = {
        'color': 'brown',
        'linewidth': 0.7,
        'linestyle': '-',
        'marker': '.',
        'markersize': 2,
        # 'capsize':4,
    }
    hcl_on_plot_cfg = {
        'color': 'cyan',
        'linewidth': 1,
        'linestyle': '-',
        'marker': '.',
        'markersize': 2,

    }
    hcl_off_plot_cfg = {
        'color': 'blue',
        'linewidth': 1,
        'linestyle': '-',
        'marker': '.',
        'markersize': 2,
    }
    idle_plot_cfg = {
        'color': 'pink',
        'linewidth': 0.5,
        'linestyle': '-',
        # 'alpha': 0,8
        # 'marker': '.',
        # 'markersize': 2,
        # 'capsize':4,
    }

    fig, axs = subplots(n_ch, 1, figsize=(10, 3*n_ch), sharex=True)
    t0_shift = min([stage['t_shift'] for stage in pumping_stages + flushing_stages])*1000

    analysis = SCS_stages[-1] if SCS_stages[-1]['Name'] == 'analysis' else None

    

    for i_ch in range(n_ch):
        axs[i_ch].text(
            0.02,
            0.98,
            SHIM_ORDER[i_ch],
            transform=axs[i_ch].transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
        )

        for stage in pumping_stages:
            t_shift = stage['t_shift']*1000 - t0_shift
            t_pumping = stage['t'] + t_shift
            v_pumping = stage['v']
            axs[i_ch].plot(t_pumping*1e-3, v_pumping[:,i_ch], **pumping_plot_cfg)
            signal_hcl_on = stage['hcl_on_data']
            axs[i_ch].plot((signal_hcl_on['t'] + t_shift)*1e-3, signal_hcl_on['v'][:,i_ch], **hcl_on_plot_cfg)
            signal_hcl_off = stage['hcl_off_data']
            axs[i_ch].plot((signal_hcl_off['t'] + t_shift)*1e-3, signal_hcl_off['v'][:,i_ch], **hcl_off_plot_cfg)

        for stage in alignment_stages:
            t_shift = stage['t_shift']*1000 - t0_shift
            t_alignment = stage['t'] + t_shift
            t_aligned = stage['t_aligned'] + t_shift
            v_alignment = stage['v']
            v_aligned = stage['v_aligned']
            vrms_aligned = stage['vrms_aligned']

            axs[i_ch].plot(t_alignment*1e-3, v_alignment[:,i_ch], **alignment_plot_cfg)
            axs[i_ch].errorbar(t_aligned*1e-3, v_aligned[i_ch], yerr=vrms_aligned[i_ch], **aligned_plot_cfg)
        
        for stage in flushing_stages:
            t_shift = stage['t_shift']*1000 - t0_shift

            t_flushing = stage['t'] + t_shift
            v_flushing = stage['v']
            axs[i_ch].plot(t_flushing*1e-3, v_flushing[:,i_ch], **flushing_plot_cfg)

        for stage in idle_stages:
            t_shift = stage['t_shift']*1000 - t0_shift
            axs[i_ch].plot((stage['t'] + t_shift)*1e-3, stage['v'][:,i_ch], **idle_plot_cfg)

        if analysis:
            # t_shift = analysis['t_shift']*1000 - t0_shift

            # t_flushed = analysis['t_flushed'] + t_shift
            # v_flushed = analysis['v_flushed']
            # vrms_flushed = analysis['vrms_flushed']
            if len(flushing_stages) > 1:
                t_shift = t0_shift/1000# + stage['t_flushed']
                axs[i_ch].plot(analysis['t_flushed'] - t_shift, analysis['v_flushed'][:,i_ch], **flushed_plot_cfg)
                
        axs[i_ch].grid()
        axs[i_ch].set_ylabel('Voltage (mV)')
            # plot flushed points




    axs[0].set_title('Flux Pumping Stages')
    axs[0].plot([], [], **flushing_plot_cfg, label='Flux flushing\n(breaking all used shims)')
    axs[0].errorbar([],[], [],**aligned_plot_cfg, label='Aligned currents\n(after breaking shim 1)')
    axs[0].plot([], [], **pumping_plot_cfg, label='Flux pumping')
    axs[0].plot([], [], **alignment_plot_cfg, label='Flux alignment\n(breaking shim 1)')
    axs[0].plot([], [], **hcl_on_plot_cfg, label='HCL on averaged samples\n(all shims recovered)')
    axs[0].plot([], [], **hcl_off_plot_cfg, label='HCL off averaged samples\n(all shims recovered)')
    if idle_stages: axs[0].plot([], [], **idle_plot_cfg, label='Flux decay observation')


    axs[0].legend(ncol=3, loc='upper center')#, bbox_to_anchor=(0.5, 1.15))
    axs[-1].set_xlabel('Time (s)')

    fig.tight_layout()

    if savepath:

        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()


def plot_stages_hs_signal(t,v,SCS_stages):
    pass

on_plot_cfg = {
        'linestyle' : '--'
    }
# off_plot_cfg = {
#         'linestyle' : '-'
#     }

pump_vs_HCL_plot_cfg = {
        'linewidth': 1,
        'linestyle': '-',
        'marker': 's',
        'markersize': 2,
        'capsize':2,
        'alpha':0.7,
    }
def plot_pumping_vs_hcl_current(analyses, savepath=None):
    # sort analyses by current
    analyses.sort(key=lambda an: an[-1].get('HCL_current', 0))
    n_ch = 0
    n_pump = 0
    # asign color based on current amplitude
    currents = []
    pump_stages_indices = []
    _analyses = []
    for i, an in enumerate(analyses):
        current = an[-1]['HCL_current']
        currents.append(current)
        n_ch = max(n_ch, an[0]['v'].shape[1])
        n_pump = max(n_pump, len([None for stage in an if stage['Name'] =='fp']))
        pump_stages_indices = [i_stage for i_stage, stage in enumerate(an) if (stage['Name'] =='fp') and (i_stage not in pump_stages_indices)]
        _analyses.append([stage for stage in an if stage['Name'] == 'fp'])
    
    analyses = _analyses
    cmap = plt.cm.get_cmap('rainbow')
    norm = plt.Normalize(min(currents), max(currents))
    def color_generator(currents):
        for current in currents:
            yield cmap(norm(current))
    colors = color_generator(currents)

    for i_pump in range(n_pump):
        fig_HCL_on, axs_HCL_on = subplots(n_ch, 1, figsize=(10, 2*n_ch), sharex=True)
        fig_HCL_off, axs_HCL_off = subplots(n_ch, 1, figsize=(10, 2*n_ch), sharex=True)
        # stage = analyses[:][i_pump]
        for i_ch in range(n_ch):
            # ensure color depends directly on the current value
            for i_an, an in enumerate(analyses):
                stage = an[i_pump]
                current = currents[i_an]
                color = cmap(norm(current))
                HCL_pulse_polarity = -1 if stage['inverted_polarity'] else 1
                t_off,v_off, vrms_off = stage['hcl_off_data'].values()
                t_on,v_on, vrms_on = stage['hcl_on_data'].values()
                
                axs_HCL_off[i_ch].errorbar(
                    t_off/1000,
                    v_off[:,i_ch],
                    yerr=vrms_off[:,i_ch],
                    color=color,
                    **pump_vs_HCL_plot_cfg,
                    )
                    
                axs_HCL_on[i_ch].errorbar(
                    t_on/1000,
                    v_on[:,i_ch],
                    yerr=vrms_on[:,i_ch],
                    color=color,
                    **pump_vs_HCL_plot_cfg,
                    )
                # axs[i_ch].plot(t_on/1000,v_on[:,i_ch], color=color)#, **on_plot_cfg, label=f'$I_{{HCL ON}}$ = {HCL_pulse_polarity * an[-1]['HCL_current']} A')
                # pass
    
        for i_ch in range(n_ch):
            
            axs_HCL_off[i_ch].set_ylabel('Voltage (mV)')
            axs_HCL_off[i_ch].grid()

            axs_HCL_on[i_ch].set_ylabel('Voltage (mV)')
            axs_HCL_on[i_ch].grid()

            axs_HCL_on[i_ch].text(
                        0.02,
                        0.98,
                        SHIM_ORDER[i_ch],
                        transform=axs_HCL_on[i_ch].transAxes,
                        fontsize=9,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
                    )
            axs_HCL_off[i_ch].text(
                        0.02,
                        0.98,
                        SHIM_ORDER[i_ch],
                        transform=axs_HCL_off[i_ch].transAxes,
                        fontsize=9,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
                    )


        axs_HCL_off[-1].set_xlabel('Time (s)')
        axs_HCL_on[-1].set_xlabel('Time (s)')

        axs_HCL_on[0].set_title('Hall voltage with recovered shims with HCL on')
        axs_HCL_off[0].set_title('Hall voltage with recovered shims with HCL off')

        fig_HCL_off.tight_layout()
        fig_HCL_on.tight_layout()
        
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        fig_HCL_off.colorbar(sm, ax=axs_HCL_off, orientation='vertical', label='HCL current (A)', pad=0.02)
        fig_HCL_on.colorbar(sm, ax=axs_HCL_on, orientation='vertical', label='HCL current (A)', pad=0.02)
        if savepath:
            root, ext = os.path.splitext(savepath)
            
            HCL_off_savepath = f"{root}_HCL_off_{i_pump}{ext}"
            fig_HCL_off.savefig(HCL_off_savepath)
            print(f"Pumping VS HCL current plot saved to {os.path.abspath(HCL_off_savepath)}")
            
            HCL_on_savepath = f"{root}_HCL_on_{i_pump}{ext}"
            fig_HCL_on.savefig(HCL_on_savepath)
            print(f"Pumping VS HCL current plot saved to {os.path.abspath(HCL_on_savepath)}")

        else:
            plt.show()
        fig_HCL_off.clear()
        fig_HCL_on.clear()
    
def plot_flux_decay(t_decay, v_decay_flush_difference, vrms_decay_flush_difference, savepath=None):
    plot_cfg = {
        # 'color': 'green',
        'linewidth': 0.5,
        'linestyle': '',
        'marker': 'o',
        'markersize': 4,
        'capsize':4,
    }

    n_ch = v_decay_flush_difference.shape[1]
    fig, axs = subplots(figsize=(12,n_ch * 2), nrows=n_ch, ncols=1, sharex=True)

    if n_ch == 1:
        axs = [axs]

    for i_ch in range(n_ch):
        axs[i_ch].errorbar(t_decay, v_decay_flush_difference[:,i_ch], yerr=vrms_decay_flush_difference[:,i_ch], **plot_cfg)
        axs[i_ch].grid()
        axs[i_ch].set_ylabel('Drop after flux flush (mV)')
    
    axs[-1].set_xlabel('Decay time (h)')
    # Set logarithmic x axis with base 2 and format ticks as normal numbers (2,4,8,...)
    axs[-1].set_xscale('log', base=2)
    # Use LogLocator to place major ticks at powers of 2 and a FuncFormatter to show plain numbers
    from matplotlib import ticker
    axs[-1].xaxis.set_major_locator(ticker.LogLocator(base=2.0))
    def _fmt(x, pos=None):
        # Format integers without exponent, fall back to generic formatting
        try:
            if abs(x - round(x)) < 1e-8:
                return str(int(round(x)))
        except Exception:
            pass
        return f"{x:g}"
    axs[-1].xaxis.set_major_formatter(ticker.FuncFormatter(_fmt))

    fig.tight_layout()

    if savepath != None:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_averaged_rep_stage_pulses(meas_results, savepath=None):
    # get profiles that do not have corresponding HS signal in the data
    time_range = info.read().get('rep_analysis',{}).get('time_range', [])
    
    SCS_profiles = meas_results[0]['SCS_profiles']
    SCS_without_HS_signal = []
    
    shims_to_plot = SHIM_ORDER.copy()
    shims_to_plot = sorted(shims_to_plot, key=shim_sort_key)

    SCS_profile_names = []
    for name, SCS_profile in SCS_profiles.items():
        
        SCS_index = int(name[3:])
        SCS_profile_names.append('SCS' + str(SCS_index))
        if f'L{SCS_index}' not in SHIM_ORDER and f'R{SCS_index}' not in SHIM_ORDER:
            SCS_without_HS_signal.append('SCS' + str(SCS_index))

    # insert SCS_without_HS_signal into Shims_to_plot based on index
    for SCS in SCS_without_HS_signal:
        SCS_index = SCS[3:]
        insert_index = 0
        for i, shim in enumerate(shims_to_plot):
            if int(shim[1:]) > int(SCS_index):
                insert_index = i
                break
            insert_index = i + 1
        shims_to_plot.insert(insert_index, SCS)

    # SCS_with_profile_idx = [int(s[3:]) for s in SCS_profiles['norm'].keys()]

    n_plots =  len(shims_to_plot)
    n_meas = len(meas_results)

    meas_pars = {
    'PC_current': [],
    'HCL_current': [],
    'Vpp': [],
    'PC_regime': [],
    'HCL_regime': [],
    }
    for result in meas_results:
        metadata = result.get('metadata', {})

        try:
            meas_pars['PC_regime'].append(metadata['SCS stages'][0]['Pumping coil operation points'][0]['HCL state']['Regime'])
            if meas_pars['PC_regime'][-1] != 'idle':
                meas_pars['PC_current'].append(metadata['SCS stages'][0]['Pumping coil operation points'][0]['HCL state']['Current'] * 1e3)
            else:
                meas_pars['PC_current'].append(None)

        except (KeyError, IndexError, TypeError):
            meas_pars['PC_current'].append(None)
        
        try:
            meas_pars['HCL_regime'].append(metadata['SCS stages'][0]['HCL operation points'][0]['HCL state']['Regime'])
            if meas_pars['HCL_regime'][-1] != 'idle':
                meas_pars['HCL_current'].append(metadata['SCS stages'][0]['HCL operation points'][0]['HCL state']['Current'] * 1e3)
            else:
                meas_pars['HCL_current'].append(None)
        except (KeyError, IndexError, TypeError):
            meas_pars['HCL_current'].append(None)
        meas_pars['Vpp'].append(metadata['SCS stages'][0]['Vpp (V)'])

    sort_order = sorted(
        range(len(meas_results)),
        key=lambda i: tuple(
            (meas_pars[key][i] is None, meas_pars[key][i])
            for key in meas_pars
        ),
    )
    meas_results = [meas_results[i] for i in sort_order]
    meas_pars = {
        key: [values[i] for i in sort_order]
        for key, values in meas_pars.items()
    }

    legend_content = {}
    static_pars = {}
    # check for parameters that change between measurements and add them to legend_content
    for key, values in meas_pars.items():
        if len(set(values)) > 1:

            if key in ['PC_current', 'HCL_current']: key = 'I_p' # exception for current
            legend_content[key] = values
        else:
            static_pars[key] = values[0]

    fig, ax = subplots(n_plots, 1, sharex=True, figsize=(10, 3*n_plots), dpi=150)
    
    if n_plots == 1: ax = [ax]

    if static_pars:
        fig.subplots_adjust(right=0.8)
        static_text = "\n".join(
            f"{key} = {value}" for key, value in static_pars.items()
        )
        fig.text(
            0.975,
            0.5,
            static_text,
            ha='center',
            va='center',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.8),
        )



    for i_plot, name in enumerate(shims_to_plot):
        if 'SCS' not in name:
            for i_meas,result in enumerate(meas_results):
                metadata = result.get('metadata', {})
                set_shimnames(metadata)
                if name not in SHIM_ORDER:
                    continue
                i_ch = SHIM_ORDER.index(name)
                legend_text = ""

                for key, values in legend_content.items():
                    if key == 'I_p':
                        legend_text += f"I_p = {values[i_meas]:.0f} mA\n"
                    elif key == 'Vpp':
                        legend_text += f"Vpp = {values[i_meas]:.1f} V\n"
                    else:
                        legend_text += f"{key} = {values[i_meas]}\n"

                legend_text = legend_text[:-1] # get rid of \n

                pulse_time = result['pulse_time']
                pulse_height_avg = result['pulse_height_avg']
                pulse_height_std = result['pulse_height_std']

                ax[i_plot].plot(
                    pulse_time[0]*1e-3,
                    pulse_height_avg[:, i_ch],
                    "-",
                    markersize=1,
                    alpha=0.7,
                    label= legend_text
                    )
                ax[i_plot].fill_between(
                    pulse_time[0]*1e-3, 
                    pulse_height_avg[:,i_ch] - pulse_height_std[:,i_ch], 
                    pulse_height_avg[:,i_ch] + pulse_height_std[:,i_ch], 
                    alpha=0.3
                    )

            ax[i_plot].set_ylabel(f'Voltage (mV)')

            SCS_name = f'SCS{int(name[1:])}'
            # plot SCS profile
            # i_scs = int(name[1:])
        else:
            SCS_name = name

        ax[i_plot].text(
            0.02,
            0.98,
            name,
            transform=ax[i_plot].transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)
            )

        if SCS_name in SCS_profiles.keys():
            ax2 = ax[i_plot].twinx()
            profile_time = SCS_profiles[SCS_name][:,0]*1e3
            profile_values = SCS_profiles[SCS_name][:,1]
            profile_time = np.array([0] + SCS_profiles[SCS_name][:, 0].tolist())
            profile_values = np.array([0] + SCS_profiles[SCS_name][:, 1].tolist())
            ax2.step(profile_time, 
                    np.array(profile_values), 
                    label=f'SCS heating profile' if i_plot == 0 else '',
                    where='post', 
                    color ='red',
                    linewidth=1,
                    alpha=0.7,
                    )
            ax2.set_ylabel(f'Duty-cycle (\\%)')
            ax2.tick_params(axis='y', colors='red')
            for _i,spine in enumerate(ax2.spines.values()):
                if _i in [1]: spine.set_edgecolor('red')

        ax[i_plot].grid()

    if time_range:
        ax[-1].set_xlim(time_range[0], time_range[1])    
    ax[-1].set_xlabel('Time (s)')
    if legend_content:
        ax[0].legend(loc='upper left', bbox_to_anchor=(1.15, 1.0), borderaxespad=0)
        # fig.tight_layout(rect=[0, 0, .95, 1])
    else:
        # fig.tight_layout()
        pass

    if savepath:
        fig.savefig(savepath, bbox_inches='tight')
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()

def plot_pulse_height_histogram(pulse_analysis, savepath=None):

    pulse_height = pulse_analysis['pulse_height']
    
    n_ch = pulse_height.shape[1]
    fig, axs = subplots(n_ch, 1, figsize=(10, 2*n_ch), sharex=True)
    if n_ch == 1: axs = [axs]

    for i_ch in range(n_ch):
        axs[i_ch].hist(pulse_height[:,i_ch], bins=30, alpha=0.7)
        axs[i_ch].set_ylabel('Counts')
        axs[i_ch].set_title(f'Pulse height histogram - {SHIM_ORDER[i_ch]}')
        axs[i_ch].grid()

    axs[-1].set_xlabel('Pulse height (mV)')
    fig.tight_layout()

    if savepath:
        fig.savefig(savepath)
        print(f"Plot saved to {os.path.abspath(savepath)}")
    else:
        plt.show()