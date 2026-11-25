"""
Script: wc_analyze_experiment

Description:
This script batch-analyses a full experiment. It processes raw data consisting of movies recorded from 
each well throughout an the experiment

Requirements:
1. Raw video data recorded for each batch/plate/well during the experiment.

Functionality:
This script iterates through each sample for each day of the experiment, performs 
counts of the populations, and returns results.

Key Steps:
1. Indicate directory for analsis.
2. Iterate through each video.
3. Analyze the video to count the number of organisms.
6. Append the results to an output CSV file.

Original code based on that published in "Wellcounter: Automated High-Throughput Phenotyping for Aquatic Microinvertebrates"
This code has been heavily modified as part of the CRITTERS project.
"""

import os

import pandas as pd

import wellcounterM

# Location of videos
data_dir = "SampleVideos" 
# Output of this analysis
outfile = "SampleVideoAnalysis.csv" 

# Initialize an empty DataFrame to collect the results
result_df = pd.DataFrame()

outpath = os.path.join(data_dir, outfile)

# Get video files only
video_files = [
    f for f in os.listdir(data_dir) 
    if os.path.isfile(os.path.join(data_dir, f)) and f.endswith('.avi')
]

# Iterate over videos
for video in video_files: # Iterate through each batch, plate and well
    print("Video file currently analyzed:")
    print(video)
    video_path = os.path.join(data_dir, video)
        
    # Calculate avg. number of organisms based on three frames of the video
    count_df, _ = wellcounterM.count_particles(video_path)      
        
    vidname = os.path.splitext(video)[0]
    treat_df = pd.DataFrame([vidname])       
        
    # Join, collect and store results
    concatenated_df = pd.concat([treat_df, count_df], axis=1) 
    result_df = pd.concat([result_df, concatenated_df], axis=0, ignore_index=True)
    
    # Save the updated results to the output file after each iteration of the inner loop
    concatenated_df.to_csv(outpath, mode='a', index=False, header=not os.path.exists(os.path.join(data_dir, outfile)))
