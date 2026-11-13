# -*- coding: utf-8 -*-
"""
Script: wc_analyze_one_sample

This software is part of the following publication:
"Wellcounter: Automated High-Throughput Phenotyping for Aquatic Microinvertebrates"
Methods in Ecology and Evolution

The latest version can be found at https://github.com/cpstelzer/wellcounter

Description:
This script can be used to count microorganisms and analyze their swimming behavior
based on a single mp4-movie. 

This script calls several functions of the wellcounter imaging and motion module.

To use this script, follow these steps:
1) Copy your mp4-file to the location specified in 'data_dir' (see below)
2) Enter the name of the video file as 'video_file'
3) To execute this script:
    activate the required conda environment by "conda activate wellcount6"
    in te wellcount6 env, type "python wc_analyze_one_sample.py"

Author: Claus-Peter Stelzer
Date: 2025-02-07
 
"""

import os
import wellcounter_imaging_module as wim

# Enter the path to the to be analyzed
#data_dir = "/Users/saoirsekelleher/Documents/Research/QAEco/Paramecium/critter_counting/videos/"  # Location of video file
data_dir = "C:\\Users\\estern\\Documents\\critter_counting\\videos"  # Location of video file
video_file = "2025_02_14_12_23_Group400_Rep1_Col2_Well82.avi"
video_path = os.path.join(data_dir, video_file)

# Calculate avg. number of organisms based on three frames of the video
count_df = wim.count_particles(video_path)     

# Print the results
print("Analysis of ", video_file, "complete:")
print(count_df) 


