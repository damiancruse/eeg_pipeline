'''
Configuration file for your experiment
'''

#### GENERAL ####

# paths to each of the types of data
raw_path = '/Users/crused/Dropbox/Python/Raw/'
epoch_path = '/Users/crused/Dropbox/Python/Epochs/'
stat_path = '/Users/crused/Dropbox/Python/Stats/'

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

#### STATS ####

# define stats paramaters here
stats_params = (
    # analysis 1
    {
    'analysis_name': 'within',   # the analysis will be saved under this name, so make it good
    'subjlist': ['S01_EB','S02_EB','S03_EB'],
    'suffix': '-epo.fif',
    'statwin': [.0, .8],
    'condnames': ['motor','non-motor'], # conditions to compare
    'stat': 'dep',                            # indep or dep
    'threshold': None,                          # empty means p<.05; for TFCE=dict(start=0, step=0.2)
    'p_accept': .05,                            # cluster threshold
    'tail': 0,                                  # tail of test; 1, 0, or -1
    'n_permutations': 200                       # at least 1000
    },
    # analysis 2
    {
    'analysis_name': 'between',   # the analysis will be saved under this name, so make it good
    'subjlist': ['S01_EB','S02_EB','S03_EB'],
    'suffix': '-epo.fif',
    'statwin': [.0, .8],
    'condnames': ['motor','non-motor'], # conditions to compare
    'threshold': None,                          # empty means p<.05; for TFCE=dict(start=0, step=0.2)
    'p_accept': .05,                            # cluster threshold
    'tail': 0,                                  # tail of test; 1, 0, or -1
    'n_permutations': 200                       # at least 1000
    })