import os.path as op
import eeg_pipeline.config as config
import mne
from mne.datasets import fetch_fsaverage 
from mne.minimum_norm import (make_inverse_operator, apply_inverse, write_inverse_operator)

filepath = config.epoch_path

# Load epochs
dat = 'S01_EB'
dat_file = op.join(filepath, dat + '-epo.fif')
epochs = mne.read_epochs(dat_file)
epochs.set_eeg_reference(projection=True) # make sure it is average referenced

# compute and save noise covariance from baseline
cov_file = op.join(filepath, dat + '-cov.fif')
noise_cov_baseline = mne.compute_covariance(epochs,tmax=0)
noise_cov_baseline.save(cov_file)

# arrange template channels for forward model
montage = mne.channels.read_montage('standard_1005', ch_names=epochs.ch_names,
                                    transform=True)
epochs.set_montage(montage)

# load the template brain and surfaces
fs_dir = fetch_fsaverage(verbose=True)
subject = 'fsaverage'
trans = op.join(fs_dir, 'bem', 'fsaverage-trans.fif')
src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')

# check coregistration between the template channels and template brain
mne.viz.plot_alignment(
    epochs.info, src=src, eeg=['original', 'projected'], trans=trans, dig=True)

# compute and save forward model
fwd_file = op.join(filepath, dat + '-fwd.fif')
fwd = mne.make_forward_solution(epochs.info, trans=trans, src=src,
                                bem=bem, eeg=True, mindist=5.0, n_jobs=1)
mne.write_forward_solution(fwd_file, fwd, overwrite=True)

# load the evoked data to do the actual source modelling
ev_file = op.join(config.evoked_path, dat + '-epo_erp_motor-ave.fif')
evokeds = mne.read_evokeds(ev_file)
evokeds[0].set_eeg_reference(projection=True) # make sure it is average referenced

# create inverse model
inv_file = op.join(filepath, dat + '-inv.fif')
inv = make_inverse_operator(evokeds[0].info, fwd, noise_cov_baseline, loose=0.2, depth=0.8)
write_inverse_operator(inv_file, inv)

# apply inverse model to data
snr = 3.0
lambda2 = 1.0 / snr ** 2
stc = apply_inverse(evokeds[0], inv, lambda2, 'dSPM', verbose=True)