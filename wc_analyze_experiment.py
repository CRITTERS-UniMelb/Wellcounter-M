# -*- coding: utf-8 -*-
"""
Script: wc_analyze_experiment

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
2. A CSV file named '...treatments.csv' containing information on which 
   batch/plate/well corresponds to which treatment. The format of this file 
   should be as follows:
    
    batch,plate,well,ac
    1,1,1,23
    1,1,2,15
    1,1,3,23
    ...
    
    (in this example the column 'ac' is a clone identification number)

Functionality:
This script iterates through each sample for each day of the experiment, performs 
analyses on the populations (including counting and motion analysis), and combines 
the results with the information on the treatments.

Key Steps:
1. Load the treatment information from 'treatments.csv'.
2. Iterate through each date within the experiment period.
3. For each batch, plate, and well, derive the path to the corresponding video file.
4. Analyze the video to count the number of organisms and perform motion analysis.
5. Combine the analysis results with the treatment information.
6. Append the results to an output CSV file.

Author: Claus-Peter Stelzer
Date: 2025-02-07

"""

import os
import pandas as pd
import wellcounter_imaging_module as wim

#main_dir = "Z:\\VAL6-2025-08-15"
#data_dir = "Z:\\VAL6-2025-08-15"  # Location of videos

main_dir = "C:\\Users\\estern\\Documents\\critter_counting\\videos\\brs"
data_dir = "C:\\Users\\estern\\Documents\\critter_counting\\videos\\brs" # Location of videos
outfile = "BRS1_testvids_2026_03_05.csv" # Output of this analysis

# Initialize an empty DataFrame to collect the results
result_df = pd.DataFrame()

outpath = os.path.join(main_dir, outfile)

# Get video files only
video_files = [
    f for f in os.listdir(data_dir) 
    if os.path.isfile(os.path.join(data_dir, f)) and f.endswith('.avi')
]

for video in video_files: # Iterate through each batch, plate and well
# Derive video path
    #video_file = f'{date}_batch{batch_no}_plate{plate_no}_well{well_no}.mp4'
    print("Video file currently analyzed:")
    print(video)
    video_path = os.path.join(data_dir, video)
        
    # Calculate avg. number of organisms based on three frames of the video
    count_df = wim.count_particles(video_path)      
        
    # Perform analysis of movement behavior
    #motion_df = wmm.perform_motion_analysis(video_path)
    vidname = os.path.splitext(video)[0]
    treat_df = pd.DataFrame([vidname])       
        
    # Join, collect and store results
    concatenated_df = pd.concat([treat_df, count_df], axis=1) # horizontal concatenation
    result_df = result_df._append(concatenated_df, ignore_index=True)
    
    # Save the updated results to the output file after each iteration of the inner loop
    concatenated_df.to_csv(outpath, mode='a', index=False, header=not os.path.exists(os.path.join(main_dir, outfile)))
