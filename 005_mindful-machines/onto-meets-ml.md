
## Datasets and notebooks

_(looking for "industrial", "manufacturing")_


Equipment Monitoring, ANN:
- https://www.kaggle.com/code/dnkumars/equipment-monitoring-ann
- Dimensions: temperature, pressure, vibration, humidity, equipment, location, faulty (binary). Examples for equipment: Turbine, Compressor, Pump etc.

ML-Powered Maintenance: Smart & Proactive
- dataset: [link](https://www.kaggle.com/datasets/nafisur/dataset-for-predictive-maintenance). Is pretty old, but popular
- It is modeled after an existing milling machine and consists of 10 000 data points from a stored as rows with 14 features in columns
- Dimensions: product types, ait temp, process temp, rotational speed, torque, tool wear, failure (target variable). Also types of failure are specified: 
    1) tool wear failure (TWF): the tool will be replaced of fail at a randomly selected tool wear time between 200 - 240 mins (120 times in our dataset). At this point in time, the tool is replaced 69 times, and fails 51 times (randomly assigned).
    2) heat dissipation failure (HDF): heat dissipation causes a process failure, if the difference between air- and process temperature is below 8.6 K and the tools rotational speed is below 1380 rpm. This is the case for 115 data points.
    3) power failure (PWF): the product of torque and rotational speed (in rad/s) equals the power required for the process. If this power is below 3500 W or above 9000 W, the process fails, which is the case 95 times in our dataset.
    4) overstrain failure (OSF): if the product of tool wear and torque exceeds 11,000 minNm for the L product variant (12,000 M, 13,000 H), the process fails due to overstrain. This is true for 98 datapoints.
    5) random failures (RNF): each process has a chance of 0,1 % to fail regardless of its process parameters. This is the case for only 5 datapoints, less than could be expected for 10,000 datapoints in our dataset.


Further datasets to explore
- casting product image data for quality inspection. [link](https://www.kaggle.com/datasets/ravirajsinh45/real-life-industrial-dataset-of-casting-product). Related notebook: [link](https://www.kaggle.com/code/koheimuramatsu/model-explainability-in-industrial-image-detection)
