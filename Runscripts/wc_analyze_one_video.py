"""
Script: wc_analyze_one_video

Description:
This script can be used to count microorganisms based on a video file.
This script calls several functions of the wellcounterM imaging module.
Outputs will be produced in the same directory as the orginal video.

To use this script, follow these steps:
1) Copy your video file to the location specified in 'data_dir' (see below)
2) Enter the name of the video file as 'video_file'
3) Ensure this file is run in the wellcounterM conda environment

Original code based on that published in "Wellcounter: Automated High-Throughput Phenotyping for Aquatic Microinvertebrates"
This code has been heavily modified as part of the CRITTERS project.
"""

import os

import wellcounterM

# Enter the path to the to be analyzed
data_dir = "SampleVideos"  # Location of video file
video_file = "2025_05_21_14_45_Temp27_Conc010_Col2_Well2.avi"
video_path = os.path.join(data_dir, video_file)

# Calculate avg. number of organisms based on three frames of the video
count_df = wellcounterM.count_particles(video_path)

# Print the results
print("Analysis of ", video_file, "complete:")
print(count_df) 


