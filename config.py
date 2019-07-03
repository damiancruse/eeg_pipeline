'''
Configuration file for your experiment
'''

#### GENERAL ####

# paths to each of the types of data
import os
cwd = os.getcwd()
raw_path = os.path.join(cwd,'Raw')
epoch_path = os.path.join(cwd,'Epochs')
evoked_path = os.path.join(cwd,'Finalised')
stat_path = os.path.join(cwd,'Stats')

#### PREPROCESSING ####

# key = the name of the trigger in the ANT data; val = the name you want to use
event_info = {
    'Stimulus/s2': 'motor',
    'Stimulus/s4': 'non-motor',    
}

# define preprocessing parameters here
preproc_params = {
    'hi_pass': .01,
    'lo_pass': 40,
    'epoch_win': [-.375,1],
    'base_win': (-.2, 0)
}


#### FINALISE ####

finalise_params = (
    # finalise 1
    {
        'subjlist': ['S01_EB', 'S02_EB', 'S03_EB', 'S04_EB', 'S05_EB', 'S06_EB', 'S07_EB', 'S08_EB',
                    'S09_EB', 'S10_EB', 'S11_EB', 'S12_EB', 'S13_EB', 'S14_EB', 'S15_EB', 'S16_EB',
                    'S17_EB', 'S18_EB', 'S19_EB', 'S20_EB', 'S21_EB', 'S22_EB', 'S23_EB', 'S24_EB'
                    ],
        'suffix': 'erp',
        'condnames': ['motor','non-motor'], 
        'subconds': None,
        'avg_method': 'trim',
        'lo_pass': 20,
        'base_win': (-.2, 0)
    },
    # finalise 2
    {
        'subjlist': ['S01_EB', 'S02_EB', 'S03_EB', 'S04_EB', 'S05_EB', 'S06_EB', 'S07_EB', 'S08_EB',
                    'S09_EB', 'S10_EB', 'S11_EB', 'S12_EB', 'S13_EB', 'S14_EB', 'S15_EB', 'S16_EB',
                    'S17_EB', 'S18_EB', 'S19_EB', 'S20_EB', 'S21_EB', 'S22_EB', 'S23_EB', 'S24_EB'
                    ],
        'suffix': 'alpha',
        'condnames': ['motor','non-motor'],
        'bandpower': [8, 13],
        'avg_method': 'trim',
        'lo_pass': 20,
        'base_win': (-.2, 0)
    },
    # finalise 3
    {
        'subjlist': ['S01_EB', 'S02_EB', 'S03_EB', 'S04_EB', 'S05_EB', 'S06_EB', 'S07_EB', 'S08_EB',
                    'S09_EB', 'S10_EB', 'S11_EB', 'S12_EB', 'S13_EB', 'S14_EB', 'S15_EB', 'S16_EB',
                    'S17_EB', 'S18_EB', 'S19_EB', 'S20_EB', 'S21_EB', 'S22_EB', 'S23_EB', 'S24_EB'
                    ],
        'suffix': 'beta',
        'condnames': ['motor','non-motor'],
        'bandpower': [13, 30],
        'avg_method': 'trim',
        'lo_pass': 20,
        'base_win': (-.2, 0)
    },
)


#### STATS ####

# define stats paramaters here
stats_params = [
    # {
    #     'analysis_name': 'erp',   # the analysis will be saved under this name, so make it good        
    #     'dat0_files': [
    #         'S01_EB-epo_erp_motor-ave', 
    #         'S02_EB-epo_erp_motor-ave', 
    #         'S03_EB-epo_erp_motor-ave', 
    #         'S04_EB-epo_erp_motor-ave', 
    #         'S05_EB-epo_erp_motor-ave', 
    #         'S06_EB-epo_erp_motor-ave', 
    #         'S07_EB-epo_erp_motor-ave', 
    #         'S08_EB-epo_erp_motor-ave',
    #         'S09_EB-epo_erp_motor-ave', 
    #         'S10_EB-epo_erp_motor-ave', 
    #         'S11_EB-epo_erp_motor-ave', 
    #         'S12_EB-epo_erp_motor-ave', 
    #         'S13_EB-epo_erp_motor-ave', 
    #         'S14_EB-epo_erp_motor-ave', 
    #         'S15_EB-epo_erp_motor-ave', 
    #         'S16_EB-epo_erp_motor-ave',
    #         'S17_EB-epo_erp_motor-ave', 
    #         'S18_EB-epo_erp_motor-ave', 
    #         'S19_EB-epo_erp_motor-ave', 
    #         'S20_EB-epo_erp_motor-ave', 
    #         'S21_EB-epo_erp_motor-ave', 
    #         'S22_EB-epo_erp_motor-ave', 
    #         'S23_EB-epo_erp_motor-ave', 
    #         'S24_EB-epo_erp_motor-ave'
    #         ],
    #     'dat1_files': [
    #         'S01_EB-epo_erp_non-motor-ave', 
    #         'S02_EB-epo_erp_non-motor-ave', 
    #         'S03_EB-epo_erp_non-motor-ave', 
    #         'S04_EB-epo_erp_non-motor-ave', 
    #         'S05_EB-epo_erp_non-motor-ave', 
    #         'S06_EB-epo_erp_non-motor-ave', 
    #         'S07_EB-epo_erp_non-motor-ave', 
    #         'S08_EB-epo_erp_non-motor-ave',
    #         'S09_EB-epo_erp_non-motor-ave', 
    #         'S10_EB-epo_erp_non-motor-ave', 
    #         'S11_EB-epo_erp_non-motor-ave', 
    #         'S12_EB-epo_erp_non-motor-ave', 
    #         'S13_EB-epo_erp_non-motor-ave', 
    #         'S14_EB-epo_erp_non-motor-ave', 
    #         'S15_EB-epo_erp_non-motor-ave', 
    #         'S16_EB-epo_erp_non-motor-ave',
    #         'S17_EB-epo_erp_non-motor-ave', 
    #         'S18_EB-epo_erp_non-motor-ave', 
    #         'S19_EB-epo_erp_non-motor-ave', 
    #         'S20_EB-epo_erp_non-motor-ave', 
    #         'S21_EB-epo_erp_non-motor-ave', 
    #         'S22_EB-epo_erp_non-motor-ave', 
    #         'S23_EB-epo_erp_non-motor-ave', 
    #         'S24_EB-epo_erp_non-motor-ave'
    #         ],
    #     'statwin': [.16, .27],
    #     'condnames': ['motor','non-motor'], # Only used for plotting and storing if is a group study
    #     'stat': 'dep',                            # indep or dep
    #     'threshold': .05,  # alpha of the parametric step; for TFCE=dict(start=0, step=0.2)
    #     'p_accept': .05,                            # cluster threshold
    #     'tail': 0,                                  # tail of test; 1, 0, or -1
    #     'n_permutations': 1000                       # at least 1000
    #     },
    # {
    #     'analysis_name': 'alpha',   # the analysis will be saved under this name, so make it good        
    #     'dat0_files': [
    #         'S01_EB-epo_alpha_motor-ave', 
    #         'S02_EB-epo_alpha_motor-ave', 
    #         'S03_EB-epo_alpha_motor-ave', 
    #         'S04_EB-epo_alpha_motor-ave', 
    #         'S05_EB-epo_alpha_motor-ave', 
    #         'S06_EB-epo_alpha_motor-ave', 
    #         'S07_EB-epo_alpha_motor-ave', 
    #         'S08_EB-epo_alpha_motor-ave',
    #         'S09_EB-epo_alpha_motor-ave', 
    #         'S10_EB-epo_alpha_motor-ave', 
    #         'S11_EB-epo_alpha_motor-ave', 
    #         'S12_EB-epo_alpha_motor-ave', 
    #         'S13_EB-epo_alpha_motor-ave', 
    #         'S14_EB-epo_alpha_motor-ave', 
    #         'S15_EB-epo_alpha_motor-ave', 
    #         'S16_EB-epo_alpha_motor-ave',
    #         'S17_EB-epo_alpha_motor-ave', 
    #         'S18_EB-epo_alpha_motor-ave', 
    #         'S19_EB-epo_alpha_motor-ave', 
    #         'S20_EB-epo_alpha_motor-ave', 
    #         'S21_EB-epo_alpha_motor-ave', 
    #         'S22_EB-epo_alpha_motor-ave', 
    #         'S23_EB-epo_alpha_motor-ave', 
    #         'S24_EB-epo_alpha_motor-ave'
    #         ],
    #     'dat1_files': [
    #         'S01_EB-epo_alpha_non-motor-ave', 
    #         'S02_EB-epo_alpha_non-motor-ave', 
    #         'S03_EB-epo_alpha_non-motor-ave', 
    #         'S04_EB-epo_alpha_non-motor-ave', 
    #         'S05_EB-epo_alpha_non-motor-ave', 
    #         'S06_EB-epo_alpha_non-motor-ave', 
    #         'S07_EB-epo_alpha_non-motor-ave', 
    #         'S08_EB-epo_alpha_non-motor-ave',
    #         'S09_EB-epo_alpha_non-motor-ave', 
    #         'S10_EB-epo_alpha_non-motor-ave', 
    #         'S11_EB-epo_alpha_non-motor-ave', 
    #         'S12_EB-epo_alpha_non-motor-ave', 
    #         'S13_EB-epo_alpha_non-motor-ave', 
    #         'S14_EB-epo_alpha_non-motor-ave', 
    #         'S15_EB-epo_alpha_non-motor-ave', 
    #         'S16_EB-epo_alpha_non-motor-ave',
    #         'S17_EB-epo_alpha_non-motor-ave', 
    #         'S18_EB-epo_alpha_non-motor-ave', 
    #         'S19_EB-epo_alpha_non-motor-ave', 
    #         'S20_EB-epo_alpha_non-motor-ave', 
    #         'S21_EB-epo_alpha_non-motor-ave', 
    #         'S22_EB-epo_alpha_non-motor-ave', 
    #         'S23_EB-epo_alpha_non-motor-ave', 
    #         'S24_EB-epo_alpha_non-motor-ave'
    #         ],
    #     'statwin': [.500, .800],
    #     'condnames': ['motor','non-motor'], # Only used for plotting and storing if is a group study
    #     'stat': 'dep',                            # indep or dep
    #     'threshold': .05,  # None means p<.05 for F/t only; for TFCE=dict(start=0, step=0.2)
    #     'p_accept': .05,                            # cluster threshold
    #     'tail': -1,                                  # tail of test; 1, 0, or -1
    #     'n_permutations': 1000                       # at least 1000
    #     },
    # {
    #     'analysis_name': 'beta',   # the analysis will be saved under this name, so make it good        
    #     'dat0_files': [
    #         'S01_EB-epo_beta_motor-ave', 
    #         'S02_EB-epo_beta_motor-ave', 
    #         'S03_EB-epo_beta_motor-ave', 
    #         'S04_EB-epo_beta_motor-ave', 
    #         'S05_EB-epo_beta_motor-ave', 
    #         'S06_EB-epo_beta_motor-ave', 
    #         'S07_EB-epo_beta_motor-ave', 
    #         'S08_EB-epo_beta_motor-ave',
    #         'S09_EB-epo_beta_motor-ave', 
    #         'S10_EB-epo_beta_motor-ave', 
    #         'S11_EB-epo_beta_motor-ave', 
    #         'S12_EB-epo_beta_motor-ave', 
    #         'S13_EB-epo_beta_motor-ave', 
    #         'S14_EB-epo_beta_motor-ave', 
    #         'S15_EB-epo_beta_motor-ave', 
    #         'S16_EB-epo_beta_motor-ave',
    #         'S17_EB-epo_beta_motor-ave', 
    #         'S18_EB-epo_beta_motor-ave', 
    #         'S19_EB-epo_beta_motor-ave', 
    #         'S20_EB-epo_beta_motor-ave', 
    #         'S21_EB-epo_beta_motor-ave', 
    #         'S22_EB-epo_beta_motor-ave', 
    #         'S23_EB-epo_beta_motor-ave', 
    #         'S24_EB-epo_beta_motor-ave'
    #         ],
    #     'dat1_files': [
    #         'S01_EB-epo_beta_non-motor-ave', 
    #         'S02_EB-epo_beta_non-motor-ave', 
    #         'S03_EB-epo_beta_non-motor-ave', 
    #         'S04_EB-epo_beta_non-motor-ave', 
    #         'S05_EB-epo_beta_non-motor-ave', 
    #         'S06_EB-epo_beta_non-motor-ave', 
    #         'S07_EB-epo_beta_non-motor-ave', 
    #         'S08_EB-epo_beta_non-motor-ave',
    #         'S09_EB-epo_beta_non-motor-ave', 
    #         'S10_EB-epo_beta_non-motor-ave', 
    #         'S11_EB-epo_beta_non-motor-ave', 
    #         'S12_EB-epo_beta_non-motor-ave', 
    #         'S13_EB-epo_beta_non-motor-ave', 
    #         'S14_EB-epo_beta_non-motor-ave', 
    #         'S15_EB-epo_beta_non-motor-ave', 
    #         'S16_EB-epo_beta_non-motor-ave',
    #         'S17_EB-epo_beta_non-motor-ave', 
    #         'S18_EB-epo_beta_non-motor-ave', 
    #         'S19_EB-epo_beta_non-motor-ave', 
    #         'S20_EB-epo_beta_non-motor-ave', 
    #         'S21_EB-epo_beta_non-motor-ave', 
    #         'S22_EB-epo_beta_non-motor-ave', 
    #         'S23_EB-epo_beta_non-motor-ave', 
    #         'S24_EB-epo_beta_non-motor-ave'
    #         ],
    #     'statwin': [.1, .800],
    #     'condnames': ['motor','non-motor'], # Only used for plotting and storing if is a group study
    #     'stat': 'dep',                            # indep or dep
    #     'threshold': .05,  # None means p<.05 for F/t only; for TFCE=dict(start=0, step=0.2)
    #     'p_accept': .05,                            # cluster threshold
    #     'tail': 0,                                  # tail of test; 1, 0, or -1
    #     'n_permutations': 1000                       # at least 1000
    #     },
    {
        'analysis_name': 'single-subject',   # the analysis will be saved under this name, so make it good        
        'multi-subject': True, # i.e. we want to run the same analysis on multiple single subjects
        'dat0_files': [
            'S01_EB_alpha_motor-epo', 
            'S02_EB_alpha_motor-epo', 
            'S03_EB_alpha_motor-epo', 
            'S04_EB_alpha_motor-epo', 
            'S05_EB_alpha_motor-epo', 
            'S06_EB_alpha_motor-epo', 
            'S07_EB_alpha_motor-epo', 
            'S08_EB_alpha_motor-epo',
            'S09_EB_alpha_motor-epo', 
            'S10_EB_alpha_motor-epo', 
            'S11_EB_alpha_motor-epo', 
            'S12_EB_alpha_motor-epo', 
            'S13_EB_alpha_motor-epo', 
            'S14_EB_alpha_motor-epo', 
            'S15_EB_alpha_motor-epo', 
            'S16_EB_alpha_motor-epo',
            'S17_EB_alpha_motor-epo', 
            'S18_EB_alpha_motor-epo', 
            'S19_EB_alpha_motor-epo', 
            'S20_EB_alpha_motor-epo', 
            'S21_EB_alpha_motor-epo', 
            'S22_EB_alpha_motor-epo', 
            'S23_EB_alpha_motor-epo', 
            'S24_EB_alpha_motor-epo'
            ],
        'dat1_files': [
            'S01_EB_alpha_non-motor-epo', 
            'S02_EB_alpha_non-motor-epo', 
            'S03_EB_alpha_non-motor-epo', 
            'S04_EB_alpha_non-motor-epo', 
            'S05_EB_alpha_non-motor-epo', 
            'S06_EB_alpha_non-motor-epo', 
            'S07_EB_alpha_non-motor-epo', 
            'S08_EB_alpha_non-motor-epo',
            'S09_EB_alpha_non-motor-epo', 
            'S10_EB_alpha_non-motor-epo', 
            'S11_EB_alpha_non-motor-epo', 
            'S12_EB_alpha_non-motor-epo', 
            'S13_EB_alpha_non-motor-epo', 
            'S14_EB_alpha_non-motor-epo', 
            'S15_EB_alpha_non-motor-epo', 
            'S16_EB_alpha_non-motor-epo',
            'S17_EB_alpha_non-motor-epo', 
            'S18_EB_alpha_non-motor-epo', 
            'S19_EB_alpha_non-motor-epo', 
            'S20_EB_alpha_non-motor-epo', 
            'S21_EB_alpha_non-motor-epo', 
            'S22_EB_alpha_non-motor-epo', 
            'S23_EB_alpha_non-motor-epo', 
            'S24_EB_alpha_non-motor-epo'
            ],
        'statwin': [.500, .800],
        'condnames': ['motor','non-motor'], # Only used for plotting and storing if is a group study
        'stat': 'indep',                            # indep or dep
        'threshold': .05,  # p-value alpha for F/t only; for TFCE=dict(start=0, step=0.2)
        'p_accept': .05,                            # cluster threshold
        'tail': -1,                                  # tail of test; 1, 0, or -1
        'n_permutations': 1000                       # at least 1000
        }        
    ]   