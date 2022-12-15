#(2021) Jonathan Williams
#USAGE:
#py do_calibration.py [data_file.csv] [calibration_method] [preprocessing method] [sensor]
#calibration methods: max/min - 'mm', ellipsoid fitting - 'e'
#preprocessing methods: zscore outlier - 'o', regularization - 'r', zscore then reg - 'or', none - '-'
#sensor type: accelerometer - 'a', magnetometer - 'm' 
    
import sys
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats as st
from ellipsoid_fit import ellipsoid_fit, ellipsoid_plot, data_regularize

#z score threshold for outlier removal
ZTHRESH = 2.5
#number of divisions for spherical regularization
NDIVS = 8
#Expected radius of accelerometer spherical trace (in gs) 
ACC_MULTIPLIER = 1.0
#Expected radius of magnetometer spherical trace (in Teslas) [https://www.magnetic-declination.com/Australia/Sydney/124736.html]
MAG_MULTIPLIER = 57.0572

#Remove outliers with z-score less than z_thresh
def remove_outliers(data, z_thresh):
    z_scores = st.zscore(data)
    filtered = (np.abs(z_scores) < z_thresh).all(axis=1)
    print("{} outliers removed".format(len(data)-len(data[filtered])))
    return data[filtered]

def max_min_calibration(data, sensor_multiplier):
    u_maximums = np.array([[data[:,0].max()],[data[:,1].max()],[data[:,2].max()]])
    u_minimums = np.array([[data[:,0].min()],[data[:,1].min()],[data[:,2].min()]])
    #offset
    offset = 0.5*(u_maximums + u_minimums)
    #scalar gain
    u_differences = u_maximums - u_minimums
    u_diag = np.array([[u_differences[0,0],0.0,0.0],[0.0,u_differences[1,0],0.0],[0.0,0.0,u_differences[2,0]]])
    scale_K = 2*sensor_multiplier*np.linalg.inv(u_diag)
    
    print("MM OFFSETS: {}".format(offset))
    print("MM GAIN: {}".format(scale_K))
    #apply calibration
    data_centered = data - offset.T
    calibrated = data_centered.dot(scale_K)
    return calibrated
    
def ellipsoid_calibration(data, sensor_multiplier):
    
    center, evecs, radii, w, evals = ellipsoid_fit(data)
    #print("Ellipsoid fit coeffs: {}".format(w))    

    matrix_R = np.array([[w[0],w[3],w[4]], [w[3],w[1],w[5]], [w[4],w[5],w[2]]])/(-w[9])
    # r = [g h k].T / -L
    vec_r = np.array([[w[6]],[w[7]],[w[8]]])/(-w[9])
    
    #OFFSET:
    offset = -np.linalg.pinv(matrix_R).dot(vec_r)
    print("E Offset:{}".format(offset))    
    
    #SCALAR GAIN:
    # p = 1 - 2*offset*vec_r - offset*matrix_R*offset
    p = 1 - 2*offset.T.dot(vec_r) - offset.T.dot(matrix_R.dot(offset)) 
    scale_K_1 = np.linalg.pinv(matrix_R/p)
    scale_K_2 = np.array([[scale_K_1[0,0] ** (1/2),0.,0.],[0.,scale_K_1[1,1] ** (1/2),0.],[0.,0.,scale_K_1[2,2] ** (1/2)]])
    scale_K = np.array([[1/scale_K_2[0,0],0.,0.],[0.,1/scale_K_2[1,1],0.],[0.,0.,1/scale_K_2[2,2]]])
    print("E Scalar gain:{}".format(scale_K))
    
    #CROSS AXIS GAIN:
    matrix_Q = scale_K.dot(scale_K_1).dot(scale_K)
    psi = matrix_Q[0,1]/2
    theta = matrix_Q[0,2]/2
    phi = matrix_Q[1,2]/2
    matrix_T = np.array([[1,psi,theta],[psi,1,phi],[theta,phi,1]])
    print("E Cross axis gain:{}".format(matrix_T))
    matrix_A = np.linalg.pinv(matrix_T).dot(sensor_multiplier*scale_K)
    
    calibrated = matrix_A.dot((data - offset.T).T).T
    print("E OFFSET: {}".format(offset.T))
    print("E GAIN: {}".format(matrix_A))
    
    return calibrated

#plots the 2D ellipses and ellipses of best fit on 3 differerent planes
def plot_ellipses(data, calibrated_data, p_center, p_radii, cal_center, cal_radii, ax_lims, sensor_multiplier, file):
    figs = [plt.figure(figsize = [8,8]) for _ in range(0,3)]
    axes = [f.add_subplot(111) for f in figs]
    ax_names = ["XY", "YZ", "XZ"]
    fig_XY, fig_YZ, fig_XZ = figs
    ax_XY, ax_YZ, ax_XZ = axes

    for ax, name in zip(axes, ax_names):
        ax.set_xlim([-ax_lims,ax_lims])
        ax.set_ylim([-ax_lims,ax_lims])
        ax.set_title(name)
        ax.set_xlabel(name[0])
        ax.set_ylabel(name[1])
        ax.add_artist(plt.Circle((0,0), sensor_multiplier, fill=False, color='b'))

        unit_patch = mpatches.Patch(color='b', label='Perfect Circle')
        original_patch = mpatches.Patch(color='r', label=f"Original {name}")
        calibrated_patch = mpatches.Patch(color='g', label=f"Calibrated {name}")
        ax.legend(handles=[calibrated_patch,unit_patch,original_patch],loc="upper right")
        ax.grid(True)
    
    xy_circle = plt.Circle((p_center[0], p_center[1]), p_radii[0],fill=False, color='r')
    xy_circle_calibrated = plt.Circle((cal_center[0], cal_center[1]), cal_radii[0],fill=False, color='g')
    ax_XY.add_artist(xy_circle)
    ax_XY.add_artist(xy_circle_calibrated)
    ax_XY.scatter(calibrated_data[:,0], calibrated_data[:,1], c='g',marker='.', lw=0, alpha=1)
    ax_XY.scatter(data[:,0], data[:,1], c='r',marker='.', lw=0, alpha=1)

    yz_circle = plt.Circle((p_center[1], p_center[2]), p_radii[1],fill=False, color='r')
    yz_circle_calibrated = plt.Circle((cal_center[1], cal_center[2]), cal_radii[1],fill=False, color='g')
    ax_YZ.add_artist(yz_circle)
    ax_YZ.add_artist(yz_circle_calibrated)
    ax_YZ.scatter(calibrated_data[:,1], calibrated_data[:,2], c='g',marker='.', lw=0, alpha=1)
    ax_YZ.scatter(data[:,1], data[:,2], c='r',marker='.', lw=0, alpha=1)

    xz_circle = plt.Circle((p_center[0], p_center[2]), p_radii[2],fill=False, color='r')
    xz_circle_calibrated = plt.Circle((cal_center[0], cal_center[2]), cal_radii[2],fill=False, color='g')
    ax_XZ.add_artist(xz_circle)
    ax_XZ.add_artist(xz_circle_calibrated)
    ax_XZ.scatter(calibrated_data[:,0], calibrated_data[:,2], c='g',marker='.', lw=0, alpha=1)
    ax_XZ.scatter(data[:,0], data[:,2], c='r',marker='.', lw=0, alpha=1)

    #fig_XY.savefig(f"{file[0:-4]}_XY.png")
    #fig_XZ.savefig(f"{file[0:-4]}_XZ.png")
    #fig_YZ.savefig(f"{file[0:-4]}_YZ.png")

    return

def plotPreCalibrationEllipsoid(data,o_center, o_radii, o_evecs):
    fig_original = plt.figure(figsize = [6, 6])
    ax_original = fig_original.add_subplot(111, projection='3d')
    ax_original.scatter(data[:,0], data[:,1], data[:,2], c='b', alpha=0.5)
    ax_original.set_title('Uncalibrated Data Trace')
    ax_original.set_xlabel('x')
    ax_original.set_ylabel('y')
    ax_original.set_zlabel('z')

    #ellipsoid_plot(o_center, o_radii, o_evecs, ax=ax_original, plot_axes=True, cage_color='r')  
    #compare with calibrated data:
    #ax_original.scatter(calibrated_data[:,0], calibrated_data[:,1], calibrated_data[:,2], c='g')

    return

def plotPostCalibrationEllipsoid(data,o_center, o_radii, o_evecs, cal_center, cal_radii, cal_evecs, ax_lims):
    fig_fits = plt.figure(figsize = [6, 6])
    ax_fits= fig_fits.add_subplot(111, projection='3d')
    ax_fits.set_xlabel('x')
    ax_fits.set_ylabel('y')
    ax_fits.set_zlabel('z')
    ax_fits.set_title('Ellipsoid Fit')
    ax_fits.set_xlim3d(-ax_lims,ax_lims)
    ax_fits.set_ylim3d(-ax_lims,ax_lims)
    ax_fits.set_zlim3d(-ax_lims,ax_lims)

    ellipsoid_plot(o_center, o_radii, o_evecs, ax=ax_fits, plot_axes=True, cage_color='r')

    #plot perfect sphere for comparison
    u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:50j]
    x = sensor_multiplier * np.cos(u)*np.sin(v)
    y = sensor_multiplier * np.sin(u)*np.sin(v)
    z = sensor_multiplier * np.cos(v)
    ax_fits.plot_surface(x, y, z, color="b", alpha=0.1)

    ellipsoid_plot(cal_center, cal_radii, cal_evecs, ax=ax_fits, plot_axes=True, cage_color='g')

    original_patch = mpatches.Patch(color='r', label='Original Ellipsoid Fit')
    calibrated_patch = mpatches.Patch(color='g', label='Calibrated Ellipsoid Fit')
    unit_sphere_patch = mpatches.Patch(color='b', label='Perfect Sphere')
    ax_fits.legend(handles=[original_patch,calibrated_patch, unit_sphere_patch],loc="upper right")
    #plt.savefig('{}_ellipsoid_fit.png'.format(file_name))

    return

if __name__=='__main__':
    data_file = sys.argv[1]
    file_name = data_file[:-4]
    calibration_method = sys.argv[2]
    preprocessing = sys.argv[3]
    sensor_type = sys.argv[4]
    
    data_pd = pd.read_csv(data_file)
    print(data_file)
    z_thresh = ZTHRESH
    reg_divs = NDIVS
    
    #preprocessing methods
    if preprocessing == "o":
       data_pd = remove_outliers(data_pd, z_thresh)
       data = data_pd.to_numpy()
    elif preprocessing == "r":
       data = data_pd.to_numpy()
       data = data_regularize(data, divs=reg_divs)
    elif preprocessing == "or":
       data_pd = remove_outliers(data_pd, z_thresh)
       data = data_pd.to_numpy()
       data = data_regularize(data, divs=reg_divs)
    elif preprocessing == "-":
       data = data_pd.to_numpy()

    
    #sensor type determines axis limits on plots and radius/multiplier
    if sensor_type == "a":
        ax_lims = 1.5
        sensor_multiplier = ACC_MULTIPLIER
    elif sensor_type == "m":
        ax_lims = 90
        sensor_multiplier = MAG_MULTIPLIER #magnitude of geomagnetic field in Sydney

    #calibration method
    if calibration_method == "e":
        calibrated_data = ellipsoid_calibration(data, sensor_multiplier)
    elif calibration_method == "mm":
        calibrated_data = max_min_calibration(data, sensor_multiplier)
    else:
        print("Invalid calibration method")
        
    #Get parameters of ellipsoid fit for uncalibrated and calibrated data
    o_center, o_evecs, o_radii, p_v, _ = ellipsoid_fit(data)
    cal_center, cal_evecs, cal_radii, cal_v, _ = ellipsoid_fit(calibrated_data)

    #Plot uncalibrated 
    #plotPreCalibrationEllipsoid(data, o_center, o_radii, o_evecs)
    #Plot calibrated
    #plotPostCalibrationEllipsoid(data, o_center, o_radii, o_evecs, cal_center, cal_radii, cal_evecs, ax_lims)
    
    #Coefficient SOD statistic:
    print("Calibrated fit coefficients: {}".format(cal_v))
    sum_diff = abs(cal_v[0])-1 + abs(cal_v[1])-1 + abs(cal_v[2])-1 + abs(cal_v[3])+abs(cal_v[4])+abs(cal_v[5])+abs(cal_v[6])+abs(cal_v[7])+abs(cal_v[8])+abs(cal_v[9])**(1/2)-sensor_multiplier
    print("Coefficient SOD: "+str(format(sum_diff, '.18f')))
    
    #Uncalibrated/calibrated data projected onto 2D plots + circle of best fit
    plot_ellipses(data, calibrated_data, o_center, o_radii, cal_center, cal_radii, ax_lims, sensor_multiplier, data_file)
    #scatter_2d_plot(data,False)
    
    #Evaluation data:
    #f = open("mag_model_eval.csv", "a")
    #f.write("\"mag_8_wave.csv:mm:reg\",\"{}\",{},{}\n".format(sys.argv[1],1 if (preprocessing=='r' or preprocessing=='or') else 0,format(sum_diff,'.18f')))
    #f.close

    plt.show()
