# -*- coding: utf-8 -*-

"""
Wellcounter imaging module

This software is part of the following publication:
"Wellcounter: Automated High-Throughput Phenotyping for Aquatic Microinvertebrates"
Methods in Ecology and Evolution

The latest version can be found at https://github.com/cpstelzer/wellcounter

Description:
This module contains several low-level and high-level functions for identifying
microorganisms in the WELLCOUNTER based on recorded mp4-movies.

Note: Portions of the code in this file were generated using ChatGPT v4.0.
      All AI-generated content has been rigorously validated and tested by the 
      authors. The corresponding author accepts full responsibility for the 
      AI-assisted portions of the code.

Author: Claus-Peter Stelzer
Date: 2025-02-07

"""


import cv2
import numpy as np
import pandas as pd
import os
import yaml
import math
import string

# Function to draw grid
def draw_grid(img, grid_shape, color=(0, 255, 0), thickness=2):
    h, w, _ = img.shape
    rows, cols = grid_shape
    dy, dx = h / rows, w / cols
    overlay = np.zeros_like(img)
    
    # draw vertical lines
    for x in np.linspace(start=dx, stop=w-dx, num=cols-1):
        x = int(round(x))
        cv2.line(overlay, (x, 0), (x, h), color=color, thickness=thickness)

    # draw horizontal lines
    for y in np.linspace(start=dy, stop=h-dy, num=rows-1):
        y = int(round(y))
        cv2.line(overlay, (0, y), (w, y), color=color, thickness=thickness)

    for col_num in range(cols):
        x = int((dx/2)+dx*col_num)
        x_lab = range(30)[col_num]
        for row_num in range(rows):
            y = int((dy/2)+dy*row_num)
            y_lab = string.ascii_uppercase[row_num]
            cv2.putText(overlay, y_lab+str(x_lab), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0),2,cv2.LINE_AA)

    cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)

    return img


def add_grid_to_video(video_path):

    # Get output directory
    main_dir = os.path.dirname(video_path)
        
    # Extract the video filename without the extension
    filename = os.path.splitext(os.path.basename(video_path))[0]
        
    # Create an output path with _grid appended
    output_path = os.path.join(main_dir, f'{filename}_grid.mp4')
        
    # Open the video file
    cap = cv2.VideoCapture(video_path)
 
    # Get frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), True)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error occurred.")
            break
        
        # Add grid and write the frame to the output video file
        frame_grid = draw_grid(frame, (8,14))
        out.write(frame_grid)
 
    # Release everything
    cap.release()
    out.release()

    out_message = "Grid added to file at" + output_path

    return out_message

def read_config(config_path="wellcounter_config.yml"):
    """
    Helper-function to read the config file.
    """
    try:
        with open(config_path, "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise

def extract_frame(video_path, delay=0):
    
    """
    A low-level function to extract a specific frame from a video file.

    This function opens the video file using OpenCV, sets the video to the 
    specified frame number (delay in seconds), and reads the frame.

    Args:
        video_path (str): The path to the video file.
        delay (int): seconds since the start of the movie.

    Returns:
        ndarray: The extracted frame as an image array.
    
    """
        
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
   
    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
   
    # Calculate the frame position based on the delay
    frame_position = int(delay * cap.get(cv2.CAP_PROP_FPS))
      
    # Check if the delay is greater than the total duration of the video
    if frame_position >= total_frames:
        print("Error: Delay exceeds the total duration of the video.")
        return None
   
    # Set the frame position in the video
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
   
    # Read the frame at the specified position
    ret, frame = cap.read()
   
    # Release the video capture object
    cap.release()
    
    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read the frame at the specified delay.")
        return None
   
    # Convert the extracted frame to grayscale
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame

def process_full_video(video_path):
    """
    This function isolates the minimum, maximum, and mean frames from the video.
    
    Args:
        video_path: Filepath for video to be processed.
        firstframe: Integer for the first frame of the video to be included.
        lastframe: Integer for the last frame of the video to be included.

    Returns:
        max_frame: Image with the maximum value in any frame of the video
        min_frame: Image with the minimum value in any frame of the video
        mean_frame: The average frame of the video.
    """

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    
    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Get first frame
    first_image = extract_frame(video_path, 0)

    # Get min, max, and mean frames (using one every 10th second)
    max_frame = first_image
    min_frame = first_image
    
    # Load all frames
    frames = []
    for fid in range(total_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        min_frame = cv2.min(min_frame, frame)
        max_frame = cv2.max(max_frame, frame)
        frames.append(frame)

    # Release video
    cap.release()

    # Calculate the median and mean frames
    median_frame = np.median(frames, axis=0).astype(dtype=np.uint8)    
    mean_frame = np.mean(frames, axis=0).astype(dtype=np.uint8)

    return min_frame, max_frame, mean_frame, median_frame

def calculate_measurements(contour):
    """
        
    Calculates various particle measurements for a given contour.

    This function calculates properties such as the area, perimeter, orientation, aspect ratio, 
    solidity, eccentricity, and feret diameter for the provided contour.

    Args:
        contour (ndarray): A contour of a detected particle.

    Returns:
        list: A list of measurements including X, Y coordinates, area, perimeter, 
        orientation, aspect ratio, solidity, eccentricity, and feret diameter.
   

    """
    # Calculate measurements for a single contour
    M = cv2.moments(contour)
    
    if M["m00"] == 0:
        return None  # Avoid division by zero
    
    # Centroid coordinates, converted to integers
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    # Area and perimeter
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    try:
        # Ellipse fitting
        ellipse = cv2.fitEllipse(contour)
        orientation = ellipse[2]
        # Calculate eccentricity
        minor_axis = min(ellipse[1])
        major_axis = max(ellipse[1])
        eccentricity = np.sqrt(1 - (minor_axis ** 2) / (major_axis ** 2))
        axis_ratio = major_axis / minor_axis 
    except cv2.error as e:
        # Handling the specific error for insufficient points
        if "Incorrect size of input array" in str(e):
            orientation = np.nan
            eccentricity = np.nan
            axis_ratio = np.nan
        else:
            raise  # Re-raise the exception if it's not the expected one
    
    # Aspect ratio of bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    if (h == 0):
        aspect_ratio = np.nan
    elif (w >= h):
        aspect_ratio = float(w) / h
    elif (w < h):
        aspect_ratio = float(h) / w

    # Solidity
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area != 0 else np.nan
    
    # Feret Diameter
    (center_EC, radius_EC) = cv2.minEnclosingCircle(np.array(contour))
    feret_diameter = 2 * radius_EC

    return {
        'X': cx,
        'Y': cy,
        'area': area,
        'perimeter': perimeter,
        'orientation': orientation,
        'aspect_ratio': aspect_ratio,
        'solidity': solidity,
        'eccentricity': eccentricity,
        'feret_diameter': feret_diameter,
        'bounding_x': x,
        'bounding_y': y,
        'bounding_w': w,
        'bounding_h': h, 
        'minor_axis': minor_axis, 
        'major_axis': major_axis, 
        'axis_ratio': axis_ratio 
    }


def mask_well_area(image, first_frame):
    
    """
    This function defines an ROI (region of interest) of the size of the well. 
    All pixels outside the ROI are set to 0 (i.e., dark). 
    
    Note, this function     is called only if the wellcounter_config.yml file is set to:
        wellplate > _well_mask > True
        
    ... and it should only be used if wellplate-holders had been placed on top of 
    the six-well plates during the recordings.
        
    """
    
    # Convert image to grayscale if it is not already
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Make a threshold of entire well area
    _, threshold = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Detect the largest contour, which corresponds to the well area
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    # Create mask by filling contour on a black background
    mask = np.zeros_like(image)
    cv2.drawContours(mask, [largest_contour], 0, 1, -1)

    # Annotate the 
    cv2.drawContours(first_frame, [largest_contour], 0, (0,0,255), 4)

    return mask, first_frame

def identify_bubbles(mean_frame, well_mask, first_frame):
    """    
    This function identifies suspected bubbles in the video. 
    It returns a table of the possible bubbles and a mask of the well.
    
    Note, this function is only applied if the wellcounter_config.yml file is set to:
        masks > bubble_mask > True

    """

    # Apply well mask
    mean_masked = cv2.bitwise_and(mean_frame, mean_frame, mask = well_mask)

    # Blur mean frame
    mean_blur = cv2.medianBlur(mean_masked, 7)

    # Threshold mean frame
    _,mean_thresh = cv2.threshold(mean_blur, 200, 255, cv2.THRESH_BINARY)

    # Dilate bubbles
    kernal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    mean_dilate = cv2.dilate(mean_thresh, kernal, iterations = 5)

    # Find contours, check circularity
    bubble_contours, _ = cv2.findContours(mean_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_bubbles = []
    for cnt in bubble_contours:
        circularity = 4*math.pi*(cv2.contourArea(cnt)/cv2.arcLength(cnt, True)*cv2.arcLength(cnt, True))
        measurements = calculate_measurements(cnt)
        if circularity > 0.5:
            valid_bubbles.append(cnt)

    
    # Initialize an empty DataFrame for bubble measurements
    columns = ["X", "Y", "area", "perimeter", "orientation", "aspect_ratio", "solidity", "eccentricity",
               "feret_diameter", "bounding_x", "bounding_y", "bounding_w", "bounding_h", "minor_axis", "major_axis", "axis_ratio"]
    bubble_table = pd.DataFrame(columns=columns)
    
    if valid_bubbles:
        for contour in valid_bubbles:
            measurements = calculate_measurements(contour)
            if measurements:
                bubble_table.loc[len(bubble_table)] = measurements  # Add measurements as a new row

    # Create bubble mask
    bubble_mask = np.ones_like(mean_frame)
    cv2.drawContours(bubble_mask, valid_bubbles, -1, (0), thickness=cv2.FILLED)

    # Annotate first frame
    cv2.drawContours(first_frame, valid_bubbles, -1, (255,255,0), 3)

    return bubble_table, bubble_mask, first_frame

def analyze_microorganisms(image):
    
    """
    This function identifies microorganisms in a subtracted image (input) based 
    on parameters set in the wellcounter_config.yml file (> particle_detection), 
    specifically the parameters 'microorganism_threshold' and 'min_microorganism_area'
    
    If the parameter 'filter_by_shape' in the config file is set 'True', an optional, 
    additional filtering of the particles can done. Currently, we do not use this feature 
    in the WELLCOUNTER.
    
    Identifies microorganisms in a subtracted image based on specified parameters.

    This function processes an image to detect microorganisms using parameters 
    defined in the `wellcounter_config.yml` file, specifically the parameters 
    'microorganism_threshold' and 'min_microorganism_area'. The detection involves thresholding 
    and contour finding, followed by optional shape-based filtering of detected particles.  
    If the parameter 'filter_by_shape' in the config file is set 'True', an optional, 
    additional filtering of the particles can done. Currently, this feature is not used
    in the WELLCOUNTER. 
     
    The detected microorganisms are characterized by various morphological measurements.

    Args:
        image (ndarray): The input image in which microorganisms are to be detected.

    Returns:
        tuple: A tuple containing:
            - DataFrame: A data frame with measurements of detected microorganisms, 
            including coordinates (X, Y), area, perimeter, orientation, aspect ratio, 
            solidity, eccentricity, and feret diameter.
            - ndarray: A binary image where detected microorganisms are marked.
    
    """
        
    config=read_config()
    particle_detection_params = config['particle_detection']
    
    #print("Now within analyze_microorganisms...")
    #print("Using pixel threshold: ", particle_detection_params['microorganism_threshold'])
    #print("Using particle area: ", particle_detection_params['min_microorganism_area'])
    
    # Apply preprocessing operations for microorganism detection\
    #_, threshold = cv2.threshold(image, particle_detection_params['microorganism_threshold'], 255, cv2.THRESH_BINARY)
    threshold = cv2.inRange(image, particle_detection_params['microorganism_threshold_min'], particle_detection_params['microorganism_threshold_max'])
    threshold = cv2.medianBlur(threshold, particle_detection_params['microorganism_blur'])
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > particle_detection_params['min_microorganism_area']]
    
    # Create an empty grayscale image with the same dimensions as the original image
    binary_image = np.zeros(image.shape[:2], dtype=np.uint8)
    # Draw the filled valid contours in white
    cv2.drawContours(binary_image, valid_contours, -1, (255), thickness=cv2.FILLED)
    
    # Initialize an empty DataFrame
    columns = ["X", "Y", "area", "perimeter", "orientation", "aspect_ratio", "solidity", "eccentricity",
               "feret_diameter", "bounding_x", "bounding_y", "bounding_w", "bounding_h"]
    df = pd.DataFrame(columns=columns)
    
    if valid_contours:
        for contour in valid_contours:
            measurements = calculate_measurements(contour)
            if measurements:
                df.loc[len(df)] = measurements  # Add measurements as a new row
    
    if particle_detection_params['filter_by_shape']:
        # Filter measurements based 0.5% to 99.5% quantiles of true positive particles in the training data
        df = df[(df['eccentricity'] >= particle_detection_params['shape_min_eccentricity']) & 
                (df['eccentricity'] <= particle_detection_params['shape_max_eccentricity']) &
                (df['solidity'] >= particle_detection_params['shape_min_solidity']) & 
                (df['solidity'] <= particle_detection_params['shape_max_solidity']) &
                (df['aspect_ratio'] >= particle_detection_params['shape_min_aspectratio']) &
                (df['aspect_ratio'] <= particle_detection_params['shape_max_aspectratio']) &
                (df['perimeter'] >= particle_detection_params['shape_min_perimeter']) &
                (df['perimeter'] <= particle_detection_params['shape_max_perimeter']) &
                (df['feret_diameter'] >= particle_detection_params['shape_min_feret']) &
                (df['feret_diameter'] <= particle_detection_params['shape_max_feret']) &
                (df['area'] <= particle_detection_params['max_microorganism_area']) & 
                (df['major_axis'] <= particle_detection_params['max_majoraxis']) & 
                (df['axis_ratio'] >= particle_detection_params['min_axisratio']) & 
                (df['axis_ratio'] <= particle_detection_params['max_axisratio'])] 


    # Sort the DataFrame based on ascending Y and then X values
    df = df.sort_values(by=['Y', 'X'], ascending=[True, True])

    return df, binary_image  # Return the DataFrame and binary image of detected microorganisms



def label_particles(image, table_of_particles):
    
    """   
    Labels detected particles on an image.

    This function takes an image and a data frame containing particle information,
    in particular the X and Y coordinates of each particle, and it labels each 
    particle on the image with a colored circle.

    Args:
        image (ndarray): The input image on which particles will be labeled.
        table_of_particles (DataFrame): A data frame containing the particle information, including X and Y coordinates.

    Returns:
        ndarray: The image with labeled particles.
    
    """
    
    config = read_config()
    particle_detection_params = config['particle_detection']
    
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    sr_factor = particle_detection_params['search_radius_factor']
    dp_area = particle_detection_params['default_particle_area']
    search_radius = round(sr_factor * np.sqrt(dp_area / np.pi))
    
    if not table_of_particles.empty:
        
        for index, row in table_of_particles.iterrows():
            x, y = int(row['X']), int(row['Y'])

            cv2.circle(image, (x, y), search_radius, (0, 252, 124), thickness=3)    
            labeled_image = image
        
    else:
        labeled_image = image
     
    
    return labeled_image



def image_subtraction_from_video(median_frame, max_frame, bubble_mask, first_frame):

    # Get tracks by subtracting median from max
    range_frame = cv2.subtract(max_frame, median_frame)

    # Apply bubble filter
    range_filtered = cv2.bitwise_and(range_frame, range_frame, mask = bubble_mask)

    # Apply bilateral filter
    range_blur = cv2.bilateralFilter(range_filtered, 5, 150, 150)

    # Apply automatic threshold
    _,range_thresh = cv2.threshold(range_blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Apply dilation
    kernal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    range_dilate = cv2.dilate(range_thresh, kernal, iterations = 4)

    # Identify track contours
    track_contours, _ = cv2.findContours(range_dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    valid_tracks = []
    for cnt in track_contours:
        if cv2.arcLength(cnt, True) > 150:
            valid_tracks.append(cnt)

    # Draw track contours on max_image
    track_image = cv2.cvtColor(max_frame, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(track_image, valid_tracks, -1, (0,255,0), thickness=1)
    cv2.drawContours(first_frame, valid_tracks, -1, (255,0,255), thickness=1)

    # Create track mask
    track_mask = np.zeros_like(median_frame)
    cv2.drawContours(track_mask, valid_tracks, -1, (255), thickness=cv2.FILLED)

    # Get foreground mask
    foreground_mask = cv2.bitwise_and(median_frame, median_frame, mask = track_mask)


    return foreground_mask, track_mask, track_image, first_frame 


def image_analysis_of_frame(video_path, frame_id, well_mask, track_mask, foreground_mask):

    # Read config
    config=read_config()      
    output_params = config['outputs']

    # Load focal frame
    frame = extract_frame(video_path, frame_id)
        
    # Apply masks
    masked_image = cv2.bitwise_and(frame, frame, mask = well_mask)
    masked_image = cv2.bitwise_and(masked_image, masked_image, mask = track_mask)

    # Subtract background
    subtract_image = cv2.subtract(masked_image, foreground_mask)
    
    # Analyze microorganisms 
    table_of_particles, binary_image = analyze_microorganisms(subtract_image)
    
    if output_params['particle_detection']:
        
        # Extract the folder where the video is stored
        main_dir = os.path.dirname(video_path)
        
        # Extract the video filename without the extension
        filename = os.path.splitext(os.path.basename(video_path))[0]
        
        # Create an output folder within the folder where the video is stored
        output_path = os.path.join(main_dir, f'{filename}_particle_detection')
        
        # Create the directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # Save an image where all detected particles are labelled
        labeled_image = label_particles(frame, table_of_particles)
        cv2.imwrite(os.path.join(output_path, 'frame_' + str(frame_id) + '_particles.jpg' ), labeled_image)
                 
        # Save a table of all detected particles
        table_of_particles.to_csv(os.path.join(output_path, 'table_of_particles_' + str(frame_id) +'.csv' ), index=False)
 
    return table_of_particles

def count_particles(video_path):
    
    """
    Count and analyze microorganisms in a video.

    This function performs a high-level analysis to count microorganisms visible
    in a video. It analyzes frames from the beginning, middle, and end of the video
    to calculate the average number of microorganisms, their average size, and their
    spatial distribution in the well.

    Parameters:
    video_path (str): The file path to the input video.

    Returns:
    pd.DataFrame: A summary data frame containing the following metrics:
        - 'avg_particles': The average number of particles detected across the analyzed frames.
        - 'median_particle_size': The median size of detected particles.
        - 'spatial_nni': The average nearest neighbor index (NNI) indicating the spatial distribution of the particles.

    Raises:
    FileNotFoundError: If the specified video file does not exist.
    ValueError: If the video cannot be opened or processed.

    Workflow:
    1. The function opens the video file and calculates its duration.
    2. It determines three key frames for analysis: the beginning, middle, and near the end of the video.
    3. Each of these frames is analyzed to detect and count particles.
    4. The function computes the average number of particles, the median size of particles, and the spatial NNI.
    5. Results are printed and returned in a summary data frame.
    
    """
          
    # Calculate the duration of the video in seconds
    video = cv2.VideoCapture(video_path)
    
    # Check if the video file was opened successfully
    if not video.isOpened():
        print("Error: Could not open video file.")
        exit()
    
    # Calculate duration of the video
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)
    duration_in_seconds = total_frames / fps
    video.release()

    # Calculate the three frames to be analyzed
    frame1 = 0 # beginning of video
    frame2 = math.floor(duration_in_seconds/2) # near middle of video
    frame3 = math.floor((total_frames-1)/fps) # near end of video

    # Get first frame for annotation
    first_frame = extract_frame(video_path, frame1)
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_GRAY2BGR)

    # Process video to get minimum, maximum, and mean frames
    min_frame, max_frame, mean_frame, median_frame = process_full_video(video_path)

    # Get well mask
    well_mask, first_frame = mask_well_area(median_frame, first_frame)

    # Get bubble mask
    bubble_table, bubble_mask, first_frame = identify_bubbles(mean_frame, well_mask, first_frame)

    # Get foreground mask and tracks
    foreground_mask, track_mask, track_image, first_frame = image_subtraction_from_video(median_frame, max_frame, bubble_mask, first_frame)

    # Perform analysis on three different frames (beginning, middle and end of video)    
    table_of_particles1 = image_analysis_of_frame(video_path, frame1, well_mask, track_mask, foreground_mask)
    table_of_particles2 = image_analysis_of_frame(video_path, frame2, well_mask, track_mask, foreground_mask)
    table_of_particles3 = image_analysis_of_frame(video_path, frame3, well_mask, track_mask, foreground_mask)
        
    # Get output directory
    main_dir = os.path.dirname(video_path)
        
    # Extract the video filename without the extension
    filename = os.path.splitext(os.path.basename(video_path))[0]
        
    # Create an output folder within the folder where the video is stored
    output_path = os.path.join(main_dir, f'{filename}_particle_detection')
        
    # Create the directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
            
    # Save track image
    cv2.imwrite(os.path.join(output_path, 'frame_tracks.jpg' ), track_image)
    # Save annotated first frame
    cv2.imwrite(os.path.join(output_path, 'masked_image.jpg' ), first_frame)
    
    # Count number of bubbles
    bubble_count = bubble_table.shape[0]

    # Count detected particles
    p1 = table_of_particles1.shape[0]
    p2 = table_of_particles2.shape[0]
    p3 = table_of_particles3.shape[0]
    
    # Calculate various metrics
    avg_particles = round ( (p1+p2+p3)/3 , 1) # number of particles
    median_particle_area = table_of_particles1['area'].median()
        
    print("Individual counts: ",  p1, " ," ,p2, " ,", p3)
    print("Average number of particles: ", avg_particles)
    print("Median size of particles: ", median_particle_area)
    
    # Create a summary DataFrame
    summary_df = pd.DataFrame({
        'count1': [p1],
        'count2': [p2], 
        'count3': [p3], 
        'avg_particles': [avg_particles], # pixels/frame
        'median_particle_size': [median_particle_area], # pixels/frame
        'bubbles': bubble_count,
    })
    
    return summary_df
    

    
    
    
