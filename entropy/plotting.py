import os

import numpy as np
import scipy.stats
from scipy.interpolate import interp2d
from scipy.interpolate import spline
from scipy.stats import norm
from scipy.optimize import curve_fit

import curiosity

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from mpl_toolkits.mplot3d import Axes3D


def three_d_histogram(running_avg_ps, FIG_DIR, model_time):
    plt.figure(5)
    ax_x = plt.subplot(211)
    ax_v = plt.subplot(212, projection='3d')
    for t in range(len(running_avg_ps)):
        if (t % 10) != 0:
            continue

        running_avg_p = running_avg_ps[t]
        x_distribution = np.sum(running_avg_p, axis=1)
        v_distribution = np.sum(running_avg_p, axis=0)

        # state vs. value
        states_x = np.arange(x_distribution.shape[0])
        states_v = np.arange(v_distribution.shape[0])
        hist_states = np.zeros(shape=(len(states_x), len(states_v)))
        
        for idx in range(len(states_x)):
            for jdx in range(len(states_v)):
                x = states_x[idx]
                v = states_v[jdx]

                for tick in range(int(np.floor(running_avg_p[x][v]*1000))):
                    hist_states[x][v] += 1

        alphas_x = x_distribution.flatten()
        ax_x.plot(states_x, alphas_x)

        # n = len(states_x)                       
        # mean = sum(states_x*alphas_x)/n                  
        # sigma = sum(alphas_x*(states_x-mean)**2)/n    
        # print(sigma)
        # print(mean)

        # def gaus(x,a,x0,sigma):
        #     print(a*np.exp(-(x-x0)**2/(2*sigma**2)))
        #     return a*np.exp(-(x-x0)**2/(2*sigma**2))

        # popt,pcov = curve_fit(gaus, states_x, alphas_x, p0=[1, mean, sigma])
        # # ax_x.plot(states_x,gaus(states_x,*popt),'ro:',label='fit')
        # trial_x = np.linspace(0, n, 100)
        # ax_x.plot(trial_x, gaus(trial_x, *popt), 'r', label='fit')


        hist, xedges, yedges = np.histogram2d(hist_states[:,0], hist_states[:,1])
        xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
        xpos = xpos.flatten('F')
        ypos = ypos.flatten('F')
        zpos = np.zeros_like(xpos)

        # Construct arrays with the dimensions for the 16 bars.
        dx = 0.5 * np.ones_like(zpos)
        dy = dx.copy()
        dz = hist.flatten()

        ax_v.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b', zsort='average')

    fname = curiosity.get_next_file(FIG_DIR, model_time, "_running_avg_plot3d", ".png")
    plt.savefig(fname)


def smear_dots(running_avg_ps, FIG_DIR, model_time):
     # want to plot the running_avg_p x_distribution over time
    plt.figure(4)
    ax_x = plt.subplot(211)
    ax_v = plt.subplot(212)

    ax_x.set_xlabel('t')
    ax_v.set_xlabel('t')
    ax_x.set_ylabel('Policy distribution over x')
    ax_v.set_ylabel('Policy distribution over v')


    for t in range(len(running_avg_ps)):
        running_avg_p = running_avg_ps[t]
        x_distribution = np.sum(running_avg_p, axis=1)
        v_distribution = np.sum(running_avg_p, axis=0)

        alphas_x = x_distribution
        colors_x = np.zeros((x_distribution.shape[0],4))
        colors_x[:, 3] = alphas_x

        alphas_v = v_distribution
        colors_v = np.zeros((v_distribution.shape[0],4))
        colors_v[:, 3] = alphas_v

        ax_x.scatter(t*np.ones(shape=x_distribution.shape), x_distribution, color=colors_x)
        ax_v.scatter(t*np.ones(shape=v_distribution.shape), v_distribution, color=colors_v)
    fname = curiosity.get_next_file(FIG_DIR, model_time, "_running_avg_xv_distrs_smear_dot", ".png")
    plt.savefig(fname)

def smear_lines(running_avg_ps, FIG_DIR, model_time):
    # want to plot the running_avg_p x_distribution over time
    plt.figure(3)

    smear = plt.subplot(111)
    smear.set_xlabel('t')
    smear.set_ylabel('Policy distribution over v')

    for t in range(len(running_avg_ps)):
        running_avg_p = running_avg_ps[t]
        x_distribution = np.sum(running_avg_p, axis=1)
        v_distribution = np.sum(running_avg_p, axis=0)

        states = np.arange(x_distribution.shape[0])
        alphas = x_distribution.flatten()

        # expand data
        ls = np.linspace(0, x_distribution.shape[0], 100)
        estimate = np.interp(ls, states, alphas)

        colors = np.zeros((len(estimate),4))
        colors[:, 3] = estimate

        smear.scatter(t*np.ones(shape=(len(estimate),1)), ls, color=colors)

    fname = curiosity.get_next_file(FIG_DIR, model_time, "_running_avg_xv_distrs_smear_lines", ".png")
    plt.savefig(fname)
   
def generate_figures(env, MODEL_DIR, \
    running_avg_entropies, entropies, \
    running_avg_ps, average_ps, \
    running_avg_ps_baseline, running_avg_entropies_baseline):
    
    FIG_DIR = 'figs/' + env + '/'
    if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)
    model_time = MODEL_DIR.split('/')[1]

    # three_d_histogram(running_avg_ps, FIG_DIR, model_time)
    # smear_lines(running_avg_ps, FIG_DIR, model_time)
    # smear_dots(running_avg_ps, FIG_DIR, model_time)

    plt.figure(1)
    plt.plot(np.arange(len(running_avg_entropies)), running_avg_entropies)
    plt.plot(np.arange(len(running_avg_entropies_baseline)), running_avg_entropies_baseline)
    plt.xlabel("t")
    plt.ylabel("Running average entropy of cumulative policy")
    # plt.savefig(fname)
    plt.show()

    # fname = curiosity.get_next_file(FIG_DIR, model_time, "_entropy", ".png")    
    # plt.figure(2)
    # plt.plot(np.arange(epochs), entropies)
    # plt.xlabel("t")
    # plt.ylabel("Entropy of policy t")
    # plt.savefig(fname)
    # plt.show()

    plt.show()
