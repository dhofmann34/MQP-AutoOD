#!/bin/bash
curl -X POST -F file=@/home/tgandrews/test/MQP-AutoOD/datasets/cardio.csv -F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F detectionMethods=lof -v https://autood.wpi.edu:443/autood/index
