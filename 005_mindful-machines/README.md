
# Use cases

## Bring symbolic AI to machine learning / deep learning

The following notebook describes a pretty typical case for training a ML / DL model for predictive maintenance: `005_mindful-machines\industrial-equipment-monitoring-with-ml-onto.ipynb`

Throughout the notebook, I am describing ideas of how ontologies could enhance ML workflows.


### Datasets and notebooks

_(looking for "industrial", "manufacturing" on Kaggle)_

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
- Autonomous Supply Chain Optimizer with RL: [link](https://www.kaggle.com/code/evilspirit05/autonomous-supply-chain-optimizer-with-rl/input)


## 🚧 (under construction) Give context to telemetry

Simulate data: https://github.com/syedhassaanahmed/iot-simulator-influxdb

The case for IoT + Schema.org: [link](https://schema.org/docs/iot-gettingstarted.html)
- Further info about microdata: [link](https://www.linkedin.com/posts/volpini_%F0%9D%97%AC%F0%9D%97%BC%F0%9D%98%82%F0%9D%97%BF-%F0%9D%98%84%F0%9D%97%B2%F0%9D%97%AF%F0%9D%98%80%F0%9D%97%B6%F0%9D%98%81%F0%9D%97%B2-%F0%9D%97%B6%F0%9D%98%80-%F0%9D%97%AE%F0%9D%97%AF%F0%9D%97%BC%F0%9D%98%82%F0%9D%98%81-%F0%9D%98%81%F0%9D%97%BC-activity-7361321548714078208-QsFG)

OpenTelemetry? Something like Game of traces ([link](https://grafana.com/blog/2025/08/11/learn-opentelemetry-tracing-through-a-grand-strategy-game-introducing-game-of-traces/))?

Study standards for industrial assets: [link](https://www.linkedin.com/posts/aleksandra-kn%C3%B6dlseder-859b222b_iso14224-cfihos-reliability-activity-7367862980513869825-gMQ8)