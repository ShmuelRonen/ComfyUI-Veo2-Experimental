# ComfyUI-Veo2-Experimental

A custom node extension for ComfyUI that integrates Google's Veo 2 text-to-video generation capabilities.

![image](https://github.com/user-attachments/assets/977fff8f-5418-4904-a44b-f27435a41d55)


## Overview of Veo 2

Veo 2 is designed to generate high-quality videos from text or image prompts, supporting a variety of cinematic and visual styles. It excels in rendering intricate details across frames and offers features like real-world physics simulation and nuanced motion accuracy.

### Key Features of Veo 2

* **Text-to-Video Generation**: Create videos from descriptive text prompts
* **Resolution**: Outputs videos in 720p resolution at 24 frames per second
* **Aspect Ratios**: Supports standard formats like 16:9 and 9:16
* **Maximum Video Length**: Up to 8 seconds per video
* **Watermarking**: Videos are watermarked with SynthID for ethical AI use

## Features

- Generate videos from text prompts using Google's Veo 2 model
- Configure video aspects like duration, aspect ratio, and person generation
- Save generated videos to your output directory
- Convert Veo videos to VHS-compatible image format for further processing

## Requirements

- ComfyUI (latest version recommended)
- Google Cloud API Key with access to Veo 2
- Python 3.8+
- Google Generative AI Python SDK: `pip install google-genai`

## Installation

1. Clone this repository into your ComfyUI custom_nodes folder:
   ```
   cd /path/to/ComfyUI/custom_nodes
   git clone https://github.com/ShmuelRonen/ComfyUI-Veo2-Experimental
   ```

2. Install the Google Generative AI SDK:
   ```
   pip install google-genai
   ```

2.  Get your free API key from Google AI Studio:
   - Visit [Google AI Studio](https://aistudio.google.com/prompts/new_chat)
   - Log in with your Google account
   - Click on "Get API key" or go to settings
   - Create a new API key
   - Copy the API key for use in .env file
   - #### Create a `.env` file in the extension directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. Restart ComfyUI

## Usage

### Veo Text to Video

1. Add the "Veo Text to Video" node to your workflow
2. Enter your prompt describing the video you want to generate
3. Configure:
   - Aspect ratio (16:9 or 9:16)
   - Person generation setting (don't allow or allow adult)
   - Duration (5-8 seconds)
4. Connect to "Veo Video Saver" to view and save results

### Veo Video Saver

1. Connect video output from a Veo generation node
2. Configure:
   - Save to output (true/false)
   - Filename prefix
3. Execute to save videos to your ComfyUI output directory

### Veo to VHS

Converts Veo videos to a format compatible with other ComfyUI video processing nodes.

## Notes

- Video generation may take several minutes
- The extension implements rate limiting to avoid quota errors
- Image-to-video generation is currently not supported by Google's API
- Maximum video duration is 8 seconds

## Troubleshooting

If you encounter "Google API key is required" errors:
- Check that your `.env` file is in the correct location
- Verify your API key is valid and has access to Veo 2
- Restart ComfyUI

## License

[Your License Here]
