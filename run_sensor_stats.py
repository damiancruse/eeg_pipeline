import mne
import os.path as op
import numpy as np
from mne.stats import spatio_temporal_cluster_test, spatio_temporal_cluster_1samp_test
from mne.datasets import sample
from mne.channels import find_ch_connectivity
import eeg_pipeline.config as config
import pickle

def run_sensor_stats():
    for c in np.arange(len(config.stats_params)):
        subjlist = config.stats_params[c]['subjlist']
        condnames = config.stats_params[c]['condnames']
        tmin, tmax = config.stats_params[c]['statwin']
        nsubjs = len(subjlist)
        evokeds0 = []
        evokeds1 = []

        for subj_idx, subj in enumerate(subjlist):
            subj_file = op.join(config.epoch_path, subj + config.stats_params[c]['suffix'])
            print("Loading subject: %s" % subj_file)
            epochs = mne.read_epochs(subj_file)
            
            if subj_idx == 0:
                if nsubjs != 1:            
                    cond0_orig = np.zeros((nsubjs,len(epochs.times),epochs.info['nchan']))
                    cond1_orig = np.zeros((cond0_orig.shape))
                else:
                    cond0_orig = epochs[condnames[0]].get_data()
                    cond1_orig = epochs[condnames[1]].get_data()   

                len_tpoi = np.diff(epochs.time_as_index(config.stats_params[c]['statwin'])) + 1
                cond0 = np.zeros((cond0_orig.shape[0],len_tpoi[0],cond0_orig.shape[2]))
                cond1 = np.zeros((cond1_orig.shape[0],len_tpoi[0],cond0_orig.shape[2]))
            
            # store as evoked structure for later plotting
            ev0_temp = epochs[condnames[0]].average().filter(l_freq=None,h_freq=20).apply_baseline(config.preproc_params['base_win'])
            ev1_temp = epochs[condnames[1]].average().filter(l_freq=None,h_freq=20).apply_baseline(config.preproc_params['base_win'])
            evokeds0.append(ev0_temp)
            evokeds1.append(ev1_temp)

            if nsubjs != 1:
                cond0_orig[subj_idx] = np.transpose(ev0_temp.data)
                cond1_orig[subj_idx] = np.transpose(ev1_temp.data)
                # select time-window of interest
                ev0_temp.crop(tmin=tmin, tmax=tmax)
                ev1_temp.crop(tmin=tmin, tmax=tmax)
                cond0[subj_idx] = np.transpose(ev0_temp.data)
                cond1[subj_idx] = np.transpose(ev1_temp.data)
            else:
                cond0 = np.transpose(epochs[condnames[0]].get_data(), (0, 2, 1))
                cond1 = np.transpose(epochs[condnames[1]].get_data(), (0, 2, 1))
            
        # find electrode neighbourhoods
        connectivity = find_ch_connectivity(epochs.info, ch_type='eeg')

        # run the stats
        if config.stats_params[c]['stat'] == 'indep':
            alldata = [cond0,cond1]
            cluster_stats = spatio_temporal_cluster_test(alldata, n_permutations=config.stats_params[c]['n_permutations'],
                                                    threshold=config.stats_params[c]['threshold'], 
                                                    tail=config.stats_params[c]['tail'],
                                                    n_jobs=1, buffer_size=None,
                                                    connectivity=connectivity[0])
        elif config.stats_params[c]['stat'] == 'dep':
            # we have to use 1-sample t-tests here so also need to subtract conditions
            alldata = cond0 - cond1
            cluster_stats = spatio_temporal_cluster_1samp_test(alldata, n_permutations=config.stats_params[c]['n_permutations'],
                                                    threshold=config.stats_params[c]['threshold'], 
                                                    tail=config.stats_params[c]['tail'],
                                                    n_jobs=1, buffer_size=None,
                                                    connectivity=connectivity[0])

        # extract stats of interest
        T_obs, clusters, p_values, _ = cluster_stats
        good_cluster_inds = np.where(p_values < config.stats_params[c]['p_accept'])[0]

        # tell the user the results
        print('There are {} significant clusters'.format(good_cluster_inds.size))
        if good_cluster_inds.size != 0:
            print('p-values: {}'.format(p_values[good_cluster_inds]))
        else:
            print('Minimum p-value: {}'.format(min(p_values)))

        # some final averaging and tidying
        cond0_avg = mne.grand_average(evokeds0)
        cond1_avg = mne.grand_average(evokeds1)
        diffcond_avg = mne.combine_evoked([cond0_avg, -cond1_avg], 'equal')

        # save
        save_name = op.join(config.stat_path, config.stats_params[c]['analysis_name'] + '.dat')
        
        results = {
            'cluster_stats': cluster_stats,
            'good_cluster_inds': good_cluster_inds,
            'alldata': alldata,
            'evokeds0': evokeds0,
            'evokeds1': evokeds1
        }

        pickle_out = open(save_name,'wb')
        pickle.dump(results, pickle_out)
        pickle_out.close()