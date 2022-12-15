# IMU-Sensor-Calibration
Python program to generate static calibration factors from stationary sensor readings using the max/min or ellipsoidal method with preprocessing techniques (spherical regularization or z-score outlier removal). 

## Usage:
  `py do_calibration.py [data_file.csv] [calibration_method] [preprocessing method] [sensor]`
<p></p>
<ul> 
  <li>data file can be found in: </li>
  <li>calibration methods: max-min - 'mm', ellipsoid fitting - 'e' </li>
  <li>preprocessing methods: zscore outlier - 'o', regularization - 'r', zscore then reg - 'or', none - '-' </li>
  <li>sensor type: accelerometer - 'a', magnetometer - 'm' </li>
</ul>

## Key Results:
Unlike the max-min calibration method, the ellipsoid fitting method is able to properly calibrate a magnetometer when exposed to hard iron ferromagnetic interference from a battery. For the most accurate results using the ellipsoid fitting method, we requires atleast 10 well spread samples accross the 3 rotational axes (since we are fitting an ellipsoid with a full set of 10 coefficients). This implies that magnetometer calibration can be performed continuously whilst the IMU is running. 

Samples obtained by rotating a LSM9DS1 magnetometer while exposed to ferromagnetic interferrence from a portable battery pack:

XY axis             |  YZ axis             | XZ axis             
:-------------------------:|:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/Jon-bon-Jono/IMU-Sensor-Calibration/main/calibration_data/mag/freehand_battery_2/freehand_battery_2_XY.png)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/IMU-Sensor-Calibration/main/calibration_data/mag/freehand_battery_2/freehand_battery_2_YZ.png)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/IMU-Sensor-Calibration/main/calibration_data/mag/freehand_battery_2/freehand_battery_2_XZ.png)

Results after applying the max-min calibration method:
 
 
  `py do_calibration.py "calibration_data/mag/freehand_battery_2/freehand_battery_2.csv" 'mm' '-' 'm'`

XY axis             |  YZ axis             | XZ axis             
:-------------------------:|:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/c%2B%2B_icon.PNG)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/jupyter_logo.PNG)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/jupyter_logo.PNG)


Results after applying the ellipsoidal calibration method:


  `py do_calibration.py "calibration_data/mag/freehand_battery_2/freehand_battery_2.csv" 'e' '-' 'm'`

XY axis             |  YZ axis             | XZ axis             
:-------------------------:|:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/c%2B%2B_icon.PNG)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/jupyter_logo.PNG)  | ![](https://raw.githubusercontent.com/Jon-bon-Jono/Jon-bon-Jono.github.io/main/src/images/jupyter_logo.PNG)
