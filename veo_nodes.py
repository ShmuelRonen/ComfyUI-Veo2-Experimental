import numpy as np
import torch
import os
import cv2
import shutil
from PIL import Image
import folder_paths
from .veo_api import VeoAPI

class VeoTextToVideoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "person_generation": (["dont_allow", "allow_adult"], {"default": "dont_allow"}),
                "duration_seconds": ("INT", {"default": 8, "min": 5, "max": 8, "step": 1}),
                "api_key": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True}),
            }
        }
    
    RETURN_TYPES = ("VEO_VIDEO",)
    RETURN_NAMES = ("video_paths",)
    FUNCTION = "generate"
    CATEGORY = "video/generation"
    
    def generate(self, prompt, aspect_ratio, person_generation, duration_seconds, 
                api_key, negative_prompt=None):
        # Initialize API with provided key or environment variable
        api = VeoAPI(api_key if api_key else None)
        
        # Generate video with supported parameters
        video_paths = api.generate_video_from_text(
            prompt=prompt,
            person_generation=person_generation,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
            negative_prompt=negative_prompt,
            number_of_videos=1
        )
        
        return (video_paths,)

class VeoImageToVideoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "duration_seconds": ("INT", {"default": 8, "min": 5, "max": 8, "step": 1}),
                "api_key": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True}),
            }
        }
    
    RETURN_TYPES = ("VEO_VIDEO",)
    RETURN_NAMES = ("video_paths",)
    FUNCTION = "generate"
    CATEGORY = "video/generation"
    
    def generate(self, image, prompt, aspect_ratio, duration_seconds, 
                api_key, negative_prompt=None):
        # Convert the ComfyUI image to PIL
        image_tensor = image[0]
        i = 255. * image_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        # Initialize API with provided key or environment variable
        api = VeoAPI(api_key if api_key else None)
        
        # Generate video
        video_paths = api.generate_video_from_image(
            prompt=prompt,
            image=img,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
            negative_prompt=negative_prompt,
            number_of_videos=1
        )
        
        return (video_paths,)

class VeoVideoPreviewNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_paths": ("VEO_VIDEO",),
                "save_to_output": ("BOOLEAN", {"default": True}),
                "filename_prefix": ("STRING", {"default": "veo_video"}),
            }
        }
    
    RETURN_TYPES = ("VEO_VIDEO",)
    RETURN_NAMES = ("output_paths",)
    FUNCTION = "preview_and_save"
    CATEGORY = "video/preview"
    OUTPUT_NODE = True
    
    def preview_and_save(self, video_paths, save_to_output, filename_prefix):
        # Check if video_paths is empty
        if not video_paths:
            print("Warning: No videos were generated.")
            return ([], {"ui": {"info": "No videos were generated"}})
        
        output_paths = []
        previews = []
        
        # Process each video
        for i, video_path in enumerate(video_paths):
            # If save_to_output is enabled, copy to the output directory with the specified name
            if save_to_output:
                output_dir = folder_paths.get_output_directory()
                
                # Ensure output directory exists
                os.makedirs(output_dir, exist_ok=True)
                
                # Get file extension from the original path
                _, ext = os.path.splitext(video_path)
                
                # Create new filename with index to avoid overwriting
                counter = 1
                while True:
                    new_filename = f"{filename_prefix}_{counter:03d}{ext}"
                    output_path = os.path.join(output_dir, new_filename)
                    if not os.path.exists(output_path):
                        break
                    counter += 1
                
                # Copy the file to output directory
                try:
                    shutil.copy2(video_path, output_path)
                    output_paths.append(output_path)
                    print(f"Saved video to: {output_path}")
                except Exception as e:
                    print(f"Error saving video: {str(e)}")
                    output_paths.append(video_path)  # Use original path if save fails
            else:
                output_paths.append(video_path)
            
            # Create preview data
            preview = {
                "filename": os.path.basename(video_path if not save_to_output else output_paths[-1]),
                "subfolder": os.path.dirname(video_path if not save_to_output else output_paths[-1]),
                "type": "output" if save_to_output else "temp",
                "format": "video/mp4",  # Assuming MP4 format
                "fullpath": video_path if not save_to_output else output_paths[-1]
            }
            previews.append(preview)
        
        # Return updated paths and previews
        return (output_paths, {"ui": {"videos": previews}})

# This node converts Veo videos to VHS-compatible image format
# With fixed maximum frame count (120)
class VeoToVHS:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_paths": ("VEO_VIDEO",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "extract_frames"
    CATEGORY = "video/conversion"
    
    def extract_frames(self, video_paths):
        # Always use maximum frame count
        frame_count = 120
        
        if not video_paths:
            # Create a properly formatted dummy image for VHS
            dummy_image = torch.zeros((1, 512, 512, 3))
            return (dummy_image,)
        
        all_frames = []
        
        for video_path in video_paths:
            try:
                # Open the video file
                video = cv2.VideoCapture(video_path)
                if not video.isOpened():
                    print(f"Error: Could not open video file {video_path}")
                    continue
                
                # Get total frames and dimensions
                total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                if total_frames == 0:
                    print(f"Warning: Zero frames found in {video_path}")
                    continue
                
                width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Calculate frame step to get the requested number of frames
                frame_step = max(1, total_frames // frame_count)
                frames_to_extract = min(frame_count, total_frames)
                
                # Extract frames
                for i in range(frames_to_extract):
                    position = min(i * frame_step, total_frames - 1)
                    video.set(cv2.CAP_PROP_POS_FRAMES, position)
                    success, frame = video.read()
                    if not success:
                        break
                    
                    # Convert from BGR (OpenCV) to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PyTorch tensor in HWC format (height, width, channels)
                    # This is the format VHS expects
                    frame_tensor = torch.from_numpy(frame_rgb).float() / 255.0
                    all_frames.append(frame_tensor)
                
                # Release the video
                video.release()
                
            except Exception as e:
                print(f"Error processing video {video_path}: {str(e)}")
        
        if all_frames:
            # Stack frames in batch dimension
            result = torch.stack(all_frames, dim=0)
            return (result,)
        else:
            # Return dummy frame if extraction failed
            dummy_image = torch.zeros((1, 512, 512, 3))
            return (dummy_image,)

# Node list for registration
NODE_CLASS_MAPPINGS = {
    "VeoTextToVideo": VeoTextToVideoNode,
#    "VeoImageToVideo": VeoImageToVideoNode,
    "VeoVideoPreview": VeoVideoPreviewNode,
    "VeoToVHS": VeoToVHS
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VeoTextToVideo": "Veo Text to Video",
#    "VeoImageToVideo": "Veo Image to Video", 
    "VeoVideoPreview": "Veo Video Saver",
    "VeoToVHS": "Veo to VHS"
}