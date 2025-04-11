import time
import os
import json
import random
from google import genai
import folder_paths

class VeoAPI:
    def __init__(self, api_key=None):
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # Rate limiting settings
        self.last_request_time = 0
        self.min_request_interval = 60  # Minimum time between requests (seconds)
        self.retry_count = 3  # Number of retries for quota errors
        self.retry_delay = 120  # Delay between retries (seconds)
    
    def _wait_for_rate_limit(self):
        """Implement basic rate limiting to avoid quota errors"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            print(f"Rate limiting: Waiting {wait_time:.1f} seconds before next request...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def generate_video_from_text(self, prompt, person_generation="dont_allow", 
                                aspect_ratio="16:9", duration_seconds=8,
                                negative_prompt=None, number_of_videos=1,
                                seed=None):  # Keep parameter for compatibility
        """Generate video from text prompt using Veo 2"""
        # Create minimal config - absolutely no seed
        config = {
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration_seconds,
            "number_of_videos": number_of_videos
        }
        
        # Only add person_generation for text-to-video
        if person_generation in ["dont_allow", "allow_adult"]:
            config["person_generation"] = person_generation
        
        # Implement retries for quota errors
        retries = 0
        while retries <= self.retry_count:
            try:
                # Implement rate limiting
                self._wait_for_rate_limit()
                
                print(f"Sending request to Veo API for text-to-video generation")
                
                # Start the generation operation - ONLY these parameters
                operation = self.client.models.generate_videos(
                    model="veo-2.0-generate-001",
                    prompt=prompt,
                    config=config
                )
                
                print(f"Initial operation response: {type(operation)}")
                
                # Poll for completion
                operation_count = 0
                while not operation.done:
                    time.sleep(20)
                    operation = self.client.operations.get(operation)
                    operation_count += 1
                    print(f"Polling operation (attempt {operation_count})...")
                
                print(f"Operation completed with status: {operation.done}")
                
                # Process the response
                return self._process_video_response(operation)
                
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    # This is a quota error, retry after delay
                    retries += 1
                    if retries <= self.retry_count:
                        retry_wait = self.retry_delay * retries
                        print(f"Quota exceeded (attempt {retries}/{self.retry_count}). Waiting {retry_wait} seconds before retry...")
                        time.sleep(retry_wait)
                    else:
                        print(f"Quota exceeded after {retries} attempts. Giving up.")
                        return []
                else:
                    # Some other error occurred
                    print(f"Error generating video: {str(e)}")
                    return []
    
    def generate_video_from_image(self, prompt, image, aspect_ratio="16:9", 
                                duration_seconds=8, negative_prompt=None, 
                                number_of_videos=1, seed=None):  # Keep parameter for compatibility
        """Generate video from image and text prompt using Veo 2"""
        print("Image-to-video generation is not currently supported with your version of the Google Generative AI SDK")
        print("Please use text-to-video generation instead with a detailed prompt describing your image")
        
        # Return empty list to avoid workflow errors
        return []
    
    def _process_video_response(self, operation):
        """Process the video generation response and save videos"""
        # Save videos to ComfyUI's temp directory
        output_dir = folder_paths.get_output_directory()
        os.makedirs(output_dir, exist_ok=True)
        
        # Start with an empty videos list
        video_paths = []
        
        # Attempt to extract video data from the response
        videos_data = None
        
        # Try different response structures
        if hasattr(operation, 'response') and hasattr(operation.response, 'generated_videos'):
            videos_data = operation.response.generated_videos
            print(f"Found videos in operation.response.generated_videos")
        elif hasattr(operation, 'result') and hasattr(operation.result, 'generated_videos'):
            videos_data = operation.result.generated_videos
            print(f"Found videos in operation.result.generated_videos")
        elif hasattr(operation, 'response') and isinstance(operation.response, dict):
            if 'generated_videos' in operation.response:
                videos_data = operation.response['generated_videos']
                print(f"Found videos in operation.response['generated_videos']")
            elif 'generateVideoResponse' in operation.response:
                response_dict = operation.response['generateVideoResponse']
                if isinstance(response_dict, dict) and 'generated_videos' in response_dict:
                    videos_data = response_dict['generated_videos']
                    print(f"Found videos in operation.response['generateVideoResponse']['generated_videos']")
                else:
                    videos_data = [response_dict]
                    print(f"Found video in operation.response['generateVideoResponse']")
        
        # Try to save videos if we found them
        if videos_data:
            print(f"Found {len(videos_data)} videos to process")
            
            for n, video_data in enumerate(videos_data):
                # Create a simple filename with timestamp
                timestamp = int(time.time())
                video_path = os.path.join(output_dir, f"veo_{timestamp}_{n}.mp4")
                
                try:
                    # Try to extract and save the video
                    saved = False
                    
                    # First approach: Using video.save() directly
                    try:
                        if hasattr(video_data, 'video') and hasattr(video_data.video, 'save'):
                            video_data.video.save(video_path)
                            saved = True
                            print(f"Saved video using video.save()")
                    except Exception as e:
                        print(f"Direct save approach failed: {str(e)}")
                    
                    # Second approach: client.files.download if available
                    if not saved and hasattr(self.client, 'files') and hasattr(self.client.files, 'download'):
                        try:
                            if hasattr(video_data, 'video'):
                                self.client.files.download(file=video_data.video)
                                if hasattr(video_data.video, 'save'):
                                    video_data.video.save(video_path)
                                    saved = True
                                    print(f"Saved video using client.files.download and video.save")
                        except Exception as e:
                            print(f"Download and save approach failed: {str(e)}")
                    
                    # Third approach: Direct access to video_bytes
                    if not saved:
                        try:
                            if hasattr(video_data, 'video_bytes'):
                                with open(video_path, "wb") as f:
                                    f.write(video_data.video_bytes)
                                saved = True
                                print(f"Saved video using video_data.video_bytes")
                        except Exception as e:
                            print(f"Video bytes approach failed: {str(e)}")
                    
                    # If we managed to save the video, add it to our paths
                    if saved:
                        video_paths.append(video_path)
                    else:
                        print(f"Failed to save video {n} - could not determine the correct method")
                    
                except Exception as e:
                    print(f"Error saving video {n}: {str(e)}")
        else:
            print("No videos found in the API response")
        
        print(f"Successfully saved {len(video_paths)} videos")
        return video_paths