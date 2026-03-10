import os
import wellcounter_imaging_module as wim

# Enter the path to the video to be analyzed
#data_dir = "/Users/saoirsekelleher/Documents/Research/QAEco/Paramecium/critter_counting/videos/"  # Location of video file
data_dir = "C:\\Users\\estern\\Documents\\critter_counting\\videos\\brs" 
#data_dir = "C:\\Users\\estern\\Documents\\critter_counting\\videos"  # Location of video file
video_file = "2025_12_04_04_00_Temp18_Conc030_Col3_Well31.avi"
video_path = os.path.join(data_dir, video_file)

wim.add_grid_to_video(video_path)
