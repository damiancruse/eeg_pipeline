import mne
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mne.viz import plot_topomap
from mne.viz import plot_compare_evokeds

# configure variables for visualization
colors = {"rel_target": "crimson", "unrel_target": 'steelblue'}
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
   time_shift = epochs_orig.time_as_index(epochs.times[0])      # fix windowing shift
   diff_topo = np.mean(diff_evokeds.data[:,time_inds+time_shift],axis=1)

   # find the time points of significance
   sig_times = epochs.times[time_inds]
   
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
   plot_compare_evokeds(evokeds, title=title, picks=ch_inds, axes=ax_signals,
                        colors=colors, show=False,
                        split_legend=True, truncate_yaxis='max_ticks')

   # plot temporal cluster extent
   ymin, ymax = ax_signals.get_ylim()
   ax_signals.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                            color='orange', alpha=0.3)

   # clean up viz
   mne.viz.tight_layout(fig=fig)
   fig.subplots_adjust(bottom=.05)
   plt.show()