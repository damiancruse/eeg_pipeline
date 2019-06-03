import mne
import os.path as op
import sys
import numpy as np
from mne.stats import spatio_temporal_cluster_test, spatio_temporal_cluster_1samp_test
from mne.datasets import sample
from mne.channels import find_ch_connectivity
import eeg_pipeline.config as config
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mne.viz import plot_topomap
from mne.viz import plot_compare_evokeds

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

            epochs.interpolate_bads(reset_bads=True)
            
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
                        
            evokeds0.append(ev0_temp.copy())
            evokeds1.append(ev1_temp.copy())

            if nsubjs != 1:
                cond0_orig[subj_idx] = np.transpose(ev0_temp.data)
                cond1_orig[subj_idx] = np.transpose(ev1_temp.data)
                # select time-window of interest
                ev0_temp_crop = ev0_temp.crop(tmin=tmin, tmax=tmax)
                ev1_temp_crop = ev1_temp.crop(tmin=tmin, tmax=tmax)
                cond0[subj_idx] = np.transpose(ev0_temp_crop.data)
                cond1[subj_idx] = np.transpose(ev1_temp_crop.data)
            else:
                # select time-window of interest
                ev0_temp_crop = ev0_temp.crop(tmin=tmin, tmax=tmax)
                ev1_temp_crop = ev1_temp.crop(tmin=tmin, tmax=tmax)                
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

        # configure variables for visualization
        colors = {"motor": "crimson", "non-motor": 'steelblue'}
        # get sensor positions via layout
        pos = mne.find_layout(epochs.info).pos

        # loop over clusters
        for i_clu, clu_idx in enumerate(good_cluster_inds):
            # unpack cluster information, get unique indices
            time_inds, space_inds = np.squeeze(clusters[clu_idx])
            ch_inds = np.unique(space_inds)
            time_inds = np.unique(time_inds)   

            # get topography for F stat
            f_map = T_obs[time_inds, ...].mean(axis=0)

            # get topography of difference
            time_shift = evokeds0[c].time_as_index(tmin)      # fix windowing shift
            print('time_shift = {}'.format(time_shift))
            sig_times_idx = time_inds + time_shift
            diff_topo = np.mean(diffcond_avg.data[:,sig_times_idx],axis=1)
            sig_times = evokeds0[c].times[sig_times_idx]
            
            # create spatial mask
            mask = np.zeros((f_map.shape[0], 1), dtype=bool)
            mask[ch_inds, :] = True

            # initialize figure
            fig, ax_topo = plt.subplots(1, 1, figsize=(10, 3))

            # plot average difference and mark significant sensors
            image, _ = plot_topomap(diff_topo, pos, mask=mask, axes=ax_topo, cmap='RdBu_r',
                                    vmin=np.min, vmax=np.max, show=False)

            # create additional axes (for ERF and colorbar)
            divider = make_axes_locatable(ax_topo)

            # add axes for colorbar
            ax_colorbar = divider.append_axes('right', size='5%', pad=0.05)
            plt.colorbar(image, cax=ax_colorbar)
            ax_topo.set_xlabel(
                'Mean difference ({:0.3f} - {:0.3f} s)'.format(*sig_times[[0, -1]]))

            # add new axis for time courses and plot time courses
            ax_signals = divider.append_axes('right', size='300%', pad=1.2)
            title = 'Cluster #{0}, {1} sensor'.format(i_clu + 1, len(ch_inds))
            if len(ch_inds) > 1:
                title += "s (mean)"
            plot_compare_evokeds([cond0_avg, cond1_avg], title=title, picks=ch_inds, axes=ax_signals,
                                    colors=None, show=False,
                                    split_legend=False, truncate_yaxis='max_ticks')

            # plot temporal cluster extent
            ymin, ymax = ax_signals.get_ylim()
            ax_signals.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                                        color='orange', alpha=0.3)

            # clean up viz
            mne.viz.tight_layout(fig=fig)
            fig.subplots_adjust(bottom=.05)
            plt.show()

        

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