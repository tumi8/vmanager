#!/bin/bash
[ ! -d tmp ] && mkdir tmp
cp example.xml tmp/tmp.conf
cp test_sensoroutput.xml tmp/sensor_output.xml
python testmanager.py
