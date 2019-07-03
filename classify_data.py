import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

import mne
from mne.datasets import sample
from mne.decoding import (SlidingEstimator, GeneralizingEstimator, Scaler,
                          cross_val_multiscore, LinearModel, get_coef,
                          Vectorizer, CSP)

import os.path as op
import eeg_pipeline.config as config

filepath = config.epoch_path

test_auc = True
nperms = 200

t_by_t = False

if t_by_t:
    n_pnts = 50
else:
    n_pnts = 1

allscores = np.ndarray((n_pnts,24))
perm_allscores = np.ndarray((n_pnts,24,nperms))
max_perm_allscores = np.ndarray((24,nperms))
allscores_pval = np.ndarray((n_pnts,24))

for subj in np.arange(0,24):

    dat_file = ('S%02d_EB-epo' % (subj+1))
    dat_file = op.join(filepath, dat_file + '.fif')
    epochs = mne.read_epochs(dat_file)
    epochs.crop(tmin=0, tmax=1)
    epochs.resample(50)
    X0 = epochs['motor'].get_data()

    # dat_file = ('S%02d_EB-epo' % (subj+1))
    # dat_file = op.join(filepath, dat_file + '.fif')
    # epochs = mne.read_epochs(dat_file)
    # epochs.crop(tmin=0, tmax=1)
    # epochs.resample(50)
    X1 = epochs['non-motor'].get_data()

    X = np.concatenate((X0,X1),axis=0)
    y = np.concatenate((np.zeros(X0.shape[0]),np.ones(X1.shape[0])),axis=0)

    if t_by_t:
        clf = make_pipeline(StandardScaler(), LogisticRegression(solver='lbfgs'))
        time_decod = SlidingEstimator(clf, n_jobs=1, scoring='roc_auc', verbose=True)    
        scores = cross_val_multiscore(time_decod, X, y, cv=5, n_jobs=1)
    else:
        clf = make_pipeline(Vectorizer(), StandardScaler(), LogisticRegression(solver='lbfgs'))
        scores = cross_val_multiscore(clf, X, y, cv=5, n_jobs=1) 

    # Mean scores across cross-validation splits
    allscores[:,subj] = np.mean(scores, axis=0)
    
    if test_auc:
        for perm in np.arange(nperms):
            perm_y = np.random.permutation(y)
            if t_by_t:
                perm_clf = make_pipeline(StandardScaler(), LogisticRegression(solver='lbfgs'))
                perm_time_decod = SlidingEstimator(perm_clf, n_jobs=1, scoring='roc_auc', verbose=True)    
                perm_scores = cross_val_multiscore(perm_time_decod, X, perm_y, cv=5, n_jobs=1)
            else:
                perm_clf = make_pipeline(Vectorizer(), StandardScaler(), LogisticRegression(solver='lbfgs'))
                perm_scores = cross_val_multiscore(perm_clf, X, perm_y, cv=5, n_jobs=1)
            
            perm_allscores[:,subj,perm] = np.mean(perm_scores, axis=0)
            max_perm_allscores[subj,perm] = np.max(perm_allscores[:,subj,perm])
    
    allscores_pval[:,subj] = [np.mean(max_perm_allscores[subj,:] > allscores[t,subj]) for t in np.arange(n_pnts)]

if t_by_t:
    # Plot
    fig, ax = plt.subplots()
    ax.plot(epochs.times, np.mean(allscores,axis=1), label='score')
    ax.axhline(.5, color='k', linestyle='--', label='chance')
    ax.set_xlabel('Times')
    ax.set_ylabel('AUC')  # Area Under the Curve
    ax.legend()
    ax.axvline(.0, color='k', linestyle='-')
    ax.set_title('Sensor space decoding')
    plt.show()
    print('done')

    for subj in np.arange(0,24):
        plt.subplot(4,6,subj+1)
        plt.plot(epochs.times, allscores_pval[:,subj], label='score')
        plt.ylim((0, .2))
        plt.axhline(.05, color='k', linestyle='--', label='chance')
        plt.axvline(.0, color='k', linestyle='-')
    plt.show()
else:
    print('There were {} significant classifications'.format(np.sum(allscores_pval<.05)))