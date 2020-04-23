import os.path as op
import numpy as np
import mne
import matplotlib.pyplot as plt
from scipy import stats
import eeg_pipeline.config as config

# the main preprocess function
def preprocess(subjname):    
    # import the data
    fname = op.join(config.raw_path, subjname + '.vhdr')
    raw = mne.io.read_raw_brainvision(fname)
    raw.load_data()

    # remove the first 15-seconds as this typically has filter artifacts
    raw.crop(15,None)

    # remove channels we don't care about
    raw.drop_channels(['HEOGR','HEOGL','VEOGU','VEOGL','M1','M2'])

    # get and import electrode locations
    raw.set_montage('standard_1005')

    # create copy for use in ICA
    raw_4_ica = raw.copy()

    # filter the raw copy for ICA
    hi_pass, lo_pass = 1 , 40       # we hardcode these params for better ICA decomp
    raw_4_ica.filter(hi_pass, None)
    raw_4_ica.filter(None, lo_pass)

    # create fake epochs of the raw copy for ICA so we can reject big artifacts before decomp
    fake_event_time = np.arange(0,raw.n_times,raw.info['sfreq'])        # fake event every 1-second
    fake_event_ids = np.tile(np.array([0,1]),(fake_event_time.size,1))  # mimic the last two columns of events
    fake_events = np.column_stack((fake_event_time,fake_event_ids))
    fake_events = fake_events.astype(int)       # needs to be an array of integers
    tmin, tmax = 0, (raw_4_ica.info['sfreq']-1)/raw_4_ica.info['sfreq']
    epochs_4_ica = mne.Epochs(raw_4_ica, events=fake_events, tmin=tmin, tmax=tmax, baseline=(tmin,tmax))

    # identify bad data before running ICA
    epochs_4_ica.load_data()
    epochs_4_ica.resample(100)

    # auto reject big bad stuff before ICA
    epoch_data = epochs_4_ica.get_data()
    bad_chans, bad_trials = find_bad_data(epoch_data)

    epochs_4_ica.info['bads'] = [epochs_4_ica.info['ch_names'][i] for i in bad_chans]   
    epochs_4_ica.drop(bad_trials,'AUTO')

    # run ICA on the copy
    from mne.preprocessing import ICA
    method = 'fastica'
    decim = 3 # make it faster...
    random_state = 666 # ensures same ICA each time
    ica = ICA(method=method, random_state=random_state).fit(epochs_4_ica, decim=decim)

    # visually identify bad components
    ica.plot_components(range(0,9))     # plot only first 10 as have most variance
    comps2check = input("Indices of components to check, separated by commas [leave blank if none]:")
    if comps2check:
        comps2check_idx = list(map(int,comps2check.split(",")))
        ica.plot_properties(raw_4_ica,comps2check_idx)

    bad_comps_str = input("Indices of components to REJECT, separated by commas [leave blank if none]:")
    if bad_comps_str:
        bad_comps_idx = list(map(int,bad_comps_str.split(",")))
        ica.exclude.extend(bad_comps_idx)
        print('Removing components {}'.format(bad_comps_idx))

    # now we create the true epoch set before applying the ica to that
    # filter the raw data
    raw.filter(config.preproc_params['hi_pass'], None)
    raw.filter(None, config.preproc_params['lo_pass'])

    # extract events - BV data has markers as annotations
    events, event_id = mne.events_from_annotations(raw)

    # AWFUL HACK TO FIX TIMING PROBLEMS OF EMBODIMENT TRIGGERS £
    events[:,0] = events[:,0] - round(raw.info['sfreq']*.117)
    # END OF HACK #
    
    # rename the events to something more useful
    evt_keys = list(config.event_info.keys())
    new_event_id = {}
    for evt in evt_keys:
        new_event_id[config.event_info[evt]] = event_id[evt]

    # ANT data sometimes has duplicate triggers at exactly the same time so here we fix this
    nondup_evts = np.where(np.diff(events[:,0]) != 0)
    events = events[nondup_evts[0],:]

    # create epochs
    picks = mne.pick_types(raw.info, eeg=True,
                        stim=False, eog=False)
    tmin, tmax = config.preproc_params['epoch_win']
    baseline = config.preproc_params['base_win']
    epochs = mne.Epochs(raw, events=events, tmin=tmin, event_id=new_event_id, tmax=tmax, baseline=baseline, picks=picks)  

    # remove the bad channels identified earlier
    epochs.info['bads'] = epochs_4_ica.info['bads']

    # apply the ICA from the raw copy to the epoched data
    epochs.load_data()
    ica.apply(epochs)

    # final pass of potential bad data
    epoch_data = epochs.get_data()
    bad_chans, bad_trials = find_bad_data(epoch_data)
    epochs.info['bads'] = [epochs.info['ch_names'][i] for i in bad_chans]
    epochs.drop(bad_trials,'AUTO')

    # interpolate bad channels back into data
    epochs.interpolate_bads(reset_bads=False)

    # baseline correct again as ICA will have affected
    epochs.apply_baseline()     # with no arguments this defaults to (None,0)

    # would be good to plot and check here, but can at least plot it
    epochs.plot(scalings=dict(eeg=20e-5),n_epochs=5,n_channels=len(epochs.info['chs']),block=True)    

    # deal with any new bad channels or trials identified by user
    epochs.interpolate_bads(reset_bads=False)
    epochs.drop_bad()
    
    # put the reference channel back in
    epochs = mne.add_reference_channels(epochs,'CPz',copy=False)

    # convert to average reference
    epochs.set_eeg_reference(ref_channels='average',projection=False)

    # save the data
    fname = op.join(config.epoch_path, subjname + '-epo.fif')
    epochs.save(fname, overwrite=True)

# function to automatically find bad data
def find_bad_data(epoch_data):
    # data arrives as epochs * chans * times
    # we will follow the FASTER pipeline
    z_thresh = 3
    n_epochs = epoch_data.shape[0]
    n_chans = epoch_data.shape[1]
    n_times = epoch_data.shape[2]

    epoch_data = np.moveaxis(epoch_data,1,0)        # make chans first dimension
    epoch_data_reshape = np.reshape(epoch_data,(n_chans,n_epochs*n_times))

    # abs zscore of variance for each channel
    ch_var = np.where(np.abs(stats.zscore(np.var(epoch_data_reshape, axis=1))) > z_thresh)[0]
    # abs zscore of mean correlation with other channels
    ch_corr = np.where(np.abs(stats.zscore(np.mean(np.corrcoef(epoch_data_reshape),axis=0))) > z_thresh)[0]
    # # abs zscore of hurst exponents - this is restrictively slow so we won't bother...
    # from hurst import compute_Hc
    # ch_hurst = []
    # for ch in range(0,n_chans):
    #     print(ch)
    #     H = compute_Hc(epoch_data_reshape[ch,:], kind='change', simplified=True)[0]
    #     ch_hurst.append(H)
    # ch_hurst = np.where(np.abs(stats.zscore(ch_hurst)))

    bad_chans = np.unique(np.concatenate((ch_var,ch_corr),axis=0))
    good_chans = np.setdiff1d(np.arange(0,n_chans),bad_chans)

    # ignore the bad_chans from now on
    epoch_data_nobads = epoch_data[tuple(good_chans),:,:]

    # subtract the mean of each epoch
    epoch_data_nobads = epoch_data_nobads - np.moveaxis(np.tile(np.mean(epoch_data_nobads, axis=2),(n_times,1,1)),0,2)
    # abs zscore of mean voltage ranges
    ep_range = np.where(np.abs(stats.zscore(np.mean(np.ptp(epoch_data_nobads, axis=2), axis=0))) > z_thresh)[0]
    # abs zscore of mean voltage variance
    ep_var = np.where(np.abs(stats.zscore(np.mean(np.var(epoch_data_nobads, axis=2), axis=0))) > z_thresh)[0]
    # abs zscore of mean deviation of channels from the mean
    ep_dev = np.where(np.abs(stats.zscore(np.mean(np.mean(epoch_data_nobads, axis=2) - np.mean(np.mean(epoch_data_nobads, axis=2), axis=0), axis=0))) > z_thresh)[0]

    bad_trials = np.unique(np.concatenate((ep_range,ep_var,ep_dev),axis=0))
    # good_trials = np.setdiff1d(np.arange(0,n_epochs),bad_trials)

    return bad_chans, bad_trials