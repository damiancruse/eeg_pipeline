'''
Configuration file for your experiment
Include event name info and preprocessing parameters here
'''

loadpath = '/Users/damiancruse/Dropbox/Python/Raw/'
savepath = '/Users/damiancruse/Dropbox/Python/Epochs/'

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

# define stats paramaters here
stats_params = {
    'subjlist': [],                             # empty if single-subject
    'statwin': [.2, .6],
    'condnames': ['rel_target','unrel_target'], # conditions to compare
    'subconds': [],                             # only if group stats
    'stat': 'indep',                            # indep or dep
    'threshold': [],                          # empty means p<.05; for TFCE=dict(start=0, step=0.2)
    'p_accept': .05,                            # cluster threshold
    'tail': 1,                                  # tail of test; 1, 0, or -1
    'n_permutations': 200                       # at least 1000
}