#!/bin/bash

rm -rf build dist bcbio_monitor.* *pyc
find . -name "*pyc" -exec rm -rf {} \; 
