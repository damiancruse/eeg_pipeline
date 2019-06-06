import mne
import os.path as op
import sys
import numpy as np
from mne.stats import spatio_temporal_cluster_test, spatio_temporal_cluster_1samp_test, ttest_1samp_no_p
from mne.datasets import sample
from mne.channels import find_ch_connectivity
import eeg_pipeline.config as config
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mne.viz import plot_topomap
from mne.viz import plot_compare_evokeds
from scipy import stats as stats

def run_sensor_stats():
    for c in np.arange(len(config.stats_params)):
        dat0_files = config.stats_params[c]['dat0_files']
        dat1_files = config.stats_params[c]['dat1_files']
        condnames = config.stats_params[c]['condnames']
        tmin, tmax = config.stats_params[c]['statwin']
        
        # collect together the data to be compared
        dat0, evokeds0, connectivity = collect_data(dat0_files,condnames[0],tmin,tmax)
        dat1, evokeds1, _ = collect_data(dat1_files,condnames[1],tmin,tmax)        
        alldata = []
        
        # organise analysis parameters
        n_permutations = config.stats_params[c]['n_permutations']
        p_threshold = config.stats_params[c]['threshold']
        tail = config.stats_params[c]['tail']

        if tail == 0:
            p_threshold = p_threshold / 2
            tail_x = 1
        else:
            tail_x = tail

        # fix threshold to be one-sided if requested
        if type(p_threshold) != 'dict': # i.e. is NOT TFCE
            if config.stats_params[c]['stat'] == 'indep':
                stat_fun = ttest_ind_no_p
                if len(dat0_files) == 1: # ie is single subject stats
                    df = dat0.data.shape[0] - 1 + dat1.data.shape[0] - 1                        
                else:
                    df = len(dat0_files) - 1 + len(dat1_files) - 1                                                            
            else: # ie is dependent data, and so is one-sample t test
                # this will only ever be group data...
                # If the length of dat0_files and dat1_files are different it'll crash later anyway
                stat_fun = ttest_1samp_no_p
                df = len(dat0_files) - 1
            threshold_stat = stats.distributions.t.ppf(1. - p_threshold, df) * tail_x
        else: # i.e. is TFCE
            threshold_stat = p_threshold      
    
        # run the stats
        if config.stats_params[c]['stat'] == 'indep':
            alldata = [dat0,dat1]
            cluster_stats = spatio_temporal_cluster_test(alldata, n_permutations=n_permutations,
                                                    threshold=threshold_stat, 
                                                    tail=tail, stat_fun=stat_fun,
                                                    n_jobs=1, buffer_size=None,
                                                    connectivity=connectivity[0])
        elif config.stats_params[c]['stat'] == 'dep':
            # we have to use 1-sample t-tests here so also need to subtract conditions
            alldata = dat0 - dat1
            cluster_stats = spatio_temporal_cluster_1samp_test(alldata, n_permutations=n_permutations,
                                                    threshold=threshold_stat, 
                                                    tail=tail, stat_fun=stat_fun,
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
        if len(evokeds0) == 1:
            dat0_avg = evokeds0[0].average()
            dat1_avg = evokeds1[0].average()
        else:
            dat0_avg = mne.grand_average(evokeds0)
            dat1_avg = mne.grand_average(evokeds1)
        diffcond_avg = mne.combine_evoked([dat0_avg, -dat1_avg], 'equal')
        
        # get sensor positions via layout
        pos = mne.find_layout(evokeds0[0].info).pos

        # loop over clusters
        for i_clu, clu_idx in enumerate(good_cluster_inds):
            # unpack cluster information, get unique indices
            time_inds, space_inds = np.squeeze(clusters[clu_idx])
            ch_inds = np.unique(space_inds)
            time_inds = np.unique(time_inds)   

            # get topography for F stat
            f_map = T_obs[time_inds, ...].mean(axis=0)

            # get topography of difference
            time_shift = evokeds0[0].time_as_index(tmin)      # fix windowing shift
            print('time_shift = {}'.format(time_shift))
            sig_times_idx = time_inds + time_shift
            diff_topo = np.mean(diffcond_avg.data[:,sig_times_idx],axis=1)
            sig_times = evokeds0[0].times[sig_times_idx]
            
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
            plot_compare_evokeds([dat0_avg, dat1_avg], title=title, picks=ch_inds, axes=ax_signals,
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

def collect_data(dat0_files,condname,tmin,tmax):
    nfiles0 = len(dat0_files)
    evokeds0 = []
    # find the path to the data files
    if len(dat0_files) == 1:
        filepath = config.epoch_path
    else:
        filepath = config.evoked_path

    for dat_idx, dat in enumerate(dat0_files):
            dat_file = op.join(filepath, dat + '.fif')
            print("Loading subject: %s" % dat_file)
            # load the files first
            if nfiles0 != 1:
                ev_dat0 = mne.read_evokeds(dat_file,condition=condname)
            else:
                ev_dat0 = mne.read_epochs(dat_file)
            # We use the first dataset to create empty variables we fill in subsequently
            if dat_idx == 0:
                if nfiles0 != 1:            
                    dat0_orig = np.zeros((nfiles0,len(ev_dat0.times),ev_dat0.info['nchan']))
                else:
                    # we store all trials for single subject stats
                    dat0_orig = ev_dat0[condname].get_data()            
                # find electrode neighbourhoods
                connectivity = find_ch_connectivity(ev_dat0.info, ch_type='eeg')                                
            # store the data for later plotting
            evokeds0.append(ev_dat0.copy())

            if nfiles0 != 1:
                dat0_orig[dat_idx] = np.transpose(ev_dat0.data)
                # select time-window of interest
                ev_dat0_crop = ev_dat0.crop(tmin=tmin, tmax=tmax)
                if dat_idx == 0:
                    # create empty matrix to store the data that will actually be analysed
                    dat0 = np.zeros((dat0_orig.shape[0],ev_dat0_crop.data.shape[1],dat0_orig.shape[2]))
                dat0[dat_idx] = np.transpose(ev_dat0_crop.data)
            else:
                # select time-window of interest
                ev_dat0_crop = ev_dat0[condname].crop(tmin=tmin, tmax=tmax)
                dat0 = np.transpose(ev_dat0_crop.get_data(), (0, 2, 1))

    return dat0, evokeds0, connectivity

def ttest_ind_no_p(*args):
    tvals, _ = stats.ttest_ind(*args)
    return tvals