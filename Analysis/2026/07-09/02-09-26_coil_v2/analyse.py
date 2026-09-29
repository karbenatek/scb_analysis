from sc_break.plotter import plot_averaged_rep_stage_pulses
from utils import *
import gc_utils.info as info
from sc_break.analysis import analyse_rep_pulses, analyse_flux_decay, analyse_hcl_current_effect_on_pumping, analyse_flux_pumping_stages_indir, find_and_analyse_scs_profiles, analyse_stages_indir, analyse_stages, get_rep_stage_pulse_analysis_averaged
from sc_break.routine_fun import find_HS_reading_indir, get_HS_reading_indir
from matplotlib import pyplot as plt

# analyse_stages_indir('mount/pumping_HCL_1A', walk=1)
# analyse_stages_indir('mount/pumping_100mA', walk=1)

# analyse_hcl_current_effect_on_pumping('mount/coil/current_scan')
# analyse_hcl_current_effect_on_pumping('mount/comparison')
# analyse_stages_indir('mount/cycle_tuning', walk=1)
# analyse_stages_indir('mount/coil/04', walk=0)
# analyse_stages_indir('mount/single_scs2_pulse/redo/', walk=0)
# analyse_stages_indir('mount/single_scs1_pulse-P_current_scan/', walk=0)
# analyse_stages_indir('mount/single_scs2_pulse-P_current_scan/', walk=0)
# analyse_stages_indir('mount/single_scs2_pulse-P_current_scan/4Vpp_PC100-150mA', walk=0)
# analyse_stages_indir('mount/', walk=1)
# myfile = get_HS_reading_indir('mount/single_scs1_pulse-P_current_scan')[3]

# print(myfile)

# pulse_time, pulse_height_avg, pulse_height_std = get_rep_stage_pulse_analysis_averaged(myfile)


# for ch in range(pulse_height_avg.shape[1]):
#     plt.plot(pulse_time[0], pulse_height_avg[:,ch], label=f'Ch {ch+1}')
#     plt.fill_between(pulse_time[0], pulse_height_avg[:,ch] - pulse_height_std[:,ch], pulse_height_avg[:,ch] + pulse_height_std[:,ch], alpha=0.3)
    
# plt.show()

# analyse_rep_pulses('mount/single_scs1_pulse-P_current_scan/3V2pp')
# analyse_rep_pulses('mount/single_scs1_pulse-P_current_scan/')
# analyse_rep_pulses('mount/single_scs2_pulse-P_current_scan/')
# analyse_rep_pulses('mount/single_scs2_pulse-P_current_scan/4V5pp_PC100-150mA')
# analyse_rep_pulses('mount/single_scs2_pulse-P_current_scan/4Vpp_PC100-150mA')
# analyse_rep_pulses('mount/single_scs2_pulse-P_current_scan/4Vpp_PC100-150mA_02')
# analyse_rep_pulses('mount/single_scs2_pulse-P_current_scan/4Vpp_PC100-150mA_02')
# analyse_rep_pulses('mount/single_scs1_pulse-P_current_scan/3Vpp2_MSpulsed_wCoilBias')
# analyse_stages_indir('mount/single_scs1_pulse-P_current_scan/3Vpp2_MSpulsed_wCoilBias')
# analyse_stages_indir('mount/single_scs1_pulse-P_current_scan/5Vpp_MSpulsed_wCoilBias')
# analyse_rep_pulses('mount/single_scs1_pulse-P_current_scan/5Vpp_MSpulsed_wCoilBias')

analysis_dirs = [
    # 'mount/single_scs2_pulse-P_current_scan/5Vpp_MSpulsed_wCoilBias',
    # 'mount/single_scs2_pulse-P_current_scan/6Vpp_MSpulsed_wCoilBias',
    # 'mount/single_scs2_pulse-P_current_scan/5Vpp_mixed',
    # ['mount/single_scs1_pulse-P_current_scan/5Vpp', 'mount/single_scs1_pulse-P_current_scan/5Vpp_MSpulsed_wCoilBias'],
    # 'mount/single_scs2_pulse-P_current_scan/6Vpp_MSpulsed_wCoilBias',
    'mount/single_scs3_pulse/5Vpp_MSpulsed_wCoilBias',


    ]
for analysis_dir in analysis_dirs:
    analyse_stages_indir(analysis_dir)
    # analyse_rep_pulses(analysis_dir)

# analyse_stages_indir(analysis_dir)
# analyse_rep_pulses(analysis_dir)




# single_scs2_pulse-P_current_scan\5Vpp_MSpulsed_wCoilBias

# analyse_stages_indir('mount/single_scs2_pulseWtail/tail_val_tuning')
# analyse_stages_indir('mount/single_scs2_pulseWtail/tail_val_tuning02')
# analyse_rep_pulses('mount/single_scs2_pulseWtail/tail_val_tuning02')
