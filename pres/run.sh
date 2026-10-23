#!/bin/bash
#download data
python3 ./kod/python/download_data.py
#Clean, analyze and visualize data
python3 ./kod/python/pres.py 
python3 ./kod/python/train_iot.py

