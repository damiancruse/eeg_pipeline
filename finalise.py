import mne
import os.path as op
import sys
import numpy as np
import eeg_pipeline.config as config
import pickle
import pandas as pd

def finalise():
    # loop through all sets of finalising    
    for c in np.arange(len(config.finalise_params)):    
        # metadata to store for later reporting
        metadat = []
        # get list of subjects to work through
        subjlist = config.finalise_params[c]['subjlist']
        # work out which sort of averaging to perform
        if config.finalise_params[c]['avg_method'] == 'trim':
            # 10% trimmed mean
            from scipy.stats import trim_mean
            avg_method = lambda x: trim_mean(x, 0.1, axis=0)
        else:
            # assumes method will be set as either mean or median
            avg_method = config.finalise_params[c]['avg_method']          
        # loop through subjects
        for subj in subjlist:   
            # find and load the data
            condnames = config.finalise_params[c]['condnames']
            subj_file = op.join(config.epoch_path, subj + '-epo.fif')
            print("Loading subject: %s" % subj_file)
            epochs = mne.read_epochs(subj_file)
            # store the number of bad channels for reporting
            metadat.append({'nbads': len(epochs.info['bads'])})
            # get rid of all bad channel info as this confuses stats later
            epochs.interpolate_bads(reset_bads=True)            
            # separate out conditions of interest and create a file each
            coi = []
            for cond in condnames:
                # select the current condition
                cond_temp = epochs[cond]
                # calculate bandpower if requested
                if 'bandpower' in config.finalise_params[c]:
                    l_freq, h_freq = config.finalise_params[c]['bandpower']
                    cond_temp.filter(l_freq=l_freq,h_freq=h_freq)
                    cond_temp.apply_hilbert(envelope=True)
                    # save a version of this in case single-subject analysis wanted later
                    tf_temp = cond_temp.copy()
                    tf_temp.apply_baseline(config.finalise_params[c]['base_win'])
                    tf_save_name = (subj + '_' + config.finalise_params[c]['suffix'] + '_' + cond + '-epo.fif')
                    tf_fname = op.join(config.epoch_path,tf_save_name)
                    tf_temp.save(tf_fname)
                # average the data              
                ev_temp = cond_temp.average(method=avg_method)
                # low pass filter the average
                ev_temp.filter(l_freq=None,h_freq=config.finalise_params[c]['lo_pass'])
                # baseline correct the data
                ev_temp.apply_baseline(config.finalise_params[c]['base_win'])
                # store number of trials in each average for later reporting
                metadat[-1][cond] = ev_temp.nave
                # store it in a list in case we want to subtract any conditions
                coi.append(ev_temp.copy())                
                # save it with a sensible name
                save_name = (subj + '-epo_' + config.finalise_params[c]['suffix'] + '_' + cond + '-ave.fif')
                fname = op.join(config.evoked_path,save_name)
                ev_temp.save(fname)

            # calculate subtractions of conditions if requested
            ########
    
        # store the metadata as a CSV
        metadat_pd = pd.DataFrame(metadat)
        csv_name = op.join(config.evoked_path, config.finalise_params[c]['suffix'] + '_log.csv')
        metadat_pd.to_csv(csv_name)