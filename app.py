# Import Dependencies
import cv2
import numpy as np
import streamlit as st
import tempfile

# Function to preprocess the video frames
def preprocess_frame(frame, blur_kernel_size):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert image from BGR to grayscale
    blurred_frame = cv2.GaussianBlur(gray_frame, (blur_kernel_size, blur_kernel_size), 0) # Apply gaussian blur to frame
    return blurred_frame

# Function to compute optical flow and speed
def compute_optical_flow(prev_frame, curr_frame):
    # Calculate optical flow between the previous and current frame
    flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    # Convert coordinates from flow to polar coordinates
    magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    return magnitude

# Function to create background mask
def create_background_mask(frame, bg_subtractor, learning_rate):
    # Create background mask
    mask = bg_subtractor.apply(frame, learningRate=learning_rate)
    return mask

# Streamlit UI
st.title("Motion Speed Analysis with OpenCV")

# Video upload
uploaded_file = st.file_uploader("Upload a .mp4 video file", type=["mp4"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary file
    tfile = tempfile.NamedTemporaryFile(delete=False) # Define temp file
    tfile.write(uploaded_file.read()) # write temp file to system
    tfile.close()

    # Read video
    video_capture = cv2.VideoCapture(tfile.name)
    
    # Sliders for parameters
    blur_kernel_size = st.slider("Gaussian Blur Kernel Size", min_value=1, max_value=21, value=5, step=2)
    mask_threshold = st.slider("Mask Threshold", min_value=0, max_value=255, value=50)
    learning_rate = st.slider("Learning Rate for MOG2", min_value=0.0, max_value=1.0, value=0.1, step=0.01)

    # Background subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    # Process video frames
    frame_count = 0
    prev_frame = None
    motion_speeds = []

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Preprocess frame
        processed_frame = preprocess_frame(frame, blur_kernel_size) # Apply gaussian blur

        # Create background mask
        mask = create_background_mask(frame, bg_subtractor, learning_rate) # Create background mask
        _, mask = cv2.threshold(mask, mask_threshold, 255, cv2.THRESH_BINARY) # Apply binary threshold to mask

        # Calculate optical flow if we have a previous frame
        if prev_frame is not None:
            # Calculate optical flow between 2 frames
            speed = compute_optical_flow(prev_frame, processed_frame)
            # Calculate spped
            motion_speeds.append(np.mean(speed))

            # Overlay speed on the original frame

            # Create image that combines both original frame and frame that represents motion speed
            overlay = cv2.addWeighted(frame, 0.5, cv2.applyColorMap(np.uint8(speed), cv2.COLORMAP_JET), 0.5, 0)
            # Display blended image
            st.image(overlay, channels="BGR", caption=f"Frame {frame_count}")

        # Display mask
        st.image(mask, channels="GRAY", caption=f"Mask for Frame {frame_count}")

        # Update previous frame
        prev_frame = processed_frame
        frame_count += 1

    # Display motion speed statistics
    if motion_speeds:
        st.write(f"Minimum Speed: {np.min(motion_speeds)}")
        st.write(f"Maximum Speed: {np.max(motion_speeds)}")
        st.write(f"Average Speed: {np.mean(motion_speeds)}")

    video_capture.release()
