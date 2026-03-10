# -*- coding: utf-8 -*-
"""
Script: wc_analyze_experiment_hpc

This software is part of the following publication:
"Wellcounter: Automated High-Throughput Phenotyping for Aquatic Microinvertebrates"
Methods in Ecology and Evolution

The latest version can be found at https://github.com/cpstelzer/wellcounter

Description:
This script demonstrates the principle of batch-analyzing an entire 
WELLCOUNTER experiment. It processes raw data consisting of movies recorded from 
each batch/plate/well over consecutive days of the experiment (e.g., using 
the script 'wc_record_experiment.py'). 

Requirements:
1. Raw video data recorded for each batch/plate/well during the experiment.

Functionality:
This script iterates through each sample for each day of the experiment, performs 
analyses on the populations (including counting and motion analysis), and combines 
the results with the information on the treatments.

Key Steps:
2. Iterate through each date within the experiment period.
3. For each batch, plate, and well, derive the path to the corresponding video file.
4. Analyze the video to count the number of organisms and perform motion analysis.
5. Combine the analysis results with the treatment information.
6. Append the results to an output CSV file.

Author: Claus-Peter Stelzer
Date: 2025-02-07

Modified by Saoirse Kelleher and Eleanor Stern
Date: 2025-03-05

"""

import os
import pandas as pd
import sys
import wellcounter_imaging_module as wim

# Ingest arguments from spartan
experiment = sys.argv[1]
split = int(sys.argv[2])
experiment_mf_folder = sys.argv[3]

# Get paths for videos and outputs
data_dir = "TempVideos/Experiment_" + str(experiment) + "_" + str(split)   # Location of videos
outpath = "Outputs/Experiment_" + str(experiment) + "_" + str(split) + ".csv" # Output of this analysis

# Create temporary folder for videos
os.system('mkdir ' + '/data/scratch/projects/punim2588/' + data_dir)

# Read txt of videos for this experiment
index = open("ExperimentIndex/Experiment_" + str(experiment) + ".txt")
experiment_videos = index.readlines()

# Get video paths for this split
split_paths = experiment_videos[(split*10):((split*10)+10)]

# Download all videos
for path in split_paths:
    os.system('unimelb-mf-download --mf.config mflux.cfg --out /data/scratch/projects/punim2588/' + data_dir + " /projects/proj-2590_microcosm_experiment_videos-1128.4.1220/" + experiment_mf_folder + "/" + path.strip())

# Initialize an empty DataFrame to collect the results
result_df = pd.DataFrame()

# Get video files only
video_files = [
    f for f in os.listdir(data_dir) 
    if os.path.isfile(os.path.join(data_dir, f)) and f.endswith('.avi')
]

for video in video_files: # Iterate through each batch, plate and well
# Derive video path
    print("Video file currently analyzed:")
    print(video)
    video_path = os.path.join("/data/scratch/projects/punim2588/",data_dir, video)
        
    # Calculate avg. number of organisms based on three frames of the video
    count_df = wim.count_particles(video_path)      
        
    # Perform analysis of movement behavior
    vidname = os.path.splitext(video)[0]
    treat_df = pd.DataFrame([vidname])       
        
    # Join, collect and store results
    concatenated_df = pd.concat([treat_df, count_df], axis=1) # horizontal concatenation
    result_df = result_df._append(concatenated_df, ignore_index=True)
    
    # Save the updated results to the output file after each iteration of the inner loop
    concatenated_df.to_csv(outpath, mode='a', index=False, header=not os.path.exists(outpath))
    
    # Delete video files after processing
    os.system('rm ' + video_path)


