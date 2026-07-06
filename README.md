# STAND: A Self-Tuning Anomaly Detection System (also referred to as AutoOD)

## About STAND:
STAND is a self-tuning anomaly detection system built upon the original AutoOD methodology. STAND is designed to address the challenges of method selection and hyper-parameter tuning while remaining unsupervised. STAND frees users from the tedious manual tuning process often required for anomaly detection by intelligently identifying high likelihood inliers and outliers. STAND features a responsive visual interface allowing for seamless interaction, providing the user with insightful knowledge of how STAND operates. STAND outperforms the best unsupervised anomaly detection methods, yielding results similar to supervised methods that have access to ground truth labels.

Beyond the original AutoOD methodology, STAND introduces a rich collection of services and engineering innovations that significantly enhance usability, scalability, and maintainability. The platform features a modern, user-centered interface, support for rerunning experiments with customizable detector parameters, persistent run history, downloadable execution logs, robust error handling, and session-based management that enables multiple concurrent users. On the backend, STAND was redesigned using a layered architecture based on Flask blueprints and the factory design pattern, accompanied by a redesigned database schema to support multi-user execution. Comprehensive automated test suites, optimized SQL queries, and batch-processing improvements further increase reliability and performance, transforming the original research prototype into a robust, practical, and deployable anomaly detection platform.

The original AutoOD algorithm was published at the ACM SIGMOD/PODS International Conference on Management of Data (SIGMOD 2023): https://doi.org/10.1145/3588700
and was demoed at VLDB 2022 (48th International Conference on Very Large Databases): https://dl.acm.org/doi/abs/10.14778/3554821.3554880

**STAND is hosted at: https://autood.wpi.edu/**

This work was supported in part by NSF under grants IIS1910880, CSSI-2103832, CNS-1852498, NRT-HDR-1815866 and by
the U.S. Dept. of Education under grant P200A180088.

### STAND Architecture:
![Alt text](https://github.com/dhofmann34/AutoOD_Demo/blob/main/screenshots/architecture.jpg "AutoOD Architecture")


### Input Interface:
![Alt text](https://github.com/dhofmann34/AutoOD_Demo/blob/main/screenshots/input.png "Input Interface")
Users can upload data, provide their own anomaly detection methods, specify the column of labels, and customize the expected percentage range of anomalies in their dataset.

### Data Analytics Display:
![Alt text](https://github.com/dhofmann34/AutoOD_Demo/blob/main/screenshots/results.jpg "Data Analytics Display")
Users can filter the chart based on metrics provided and interact with points by hovering over them to view summery statistics. Clicking on a point will provide that respective point's anomaly score for each unsupervised detector and attribute values from the input dataset. In addition, by moving the slider through each iteration, the user can watch the reliable object set change, and at any time select a point to view the contribution of each detector to its status.

## Instructions:
To run STAND, download the code and fill out the "database_temp.ini" file with the information required to connect to a local PostgreSQL database. Once completed rename the file "database.ini". Now running the command "python app.py" in a terminal at the root of the project directory will lunch STAND on a local webserver.

Python version: 3.9.12 <br>
Please see requirements.txt for libraries and their versions.
