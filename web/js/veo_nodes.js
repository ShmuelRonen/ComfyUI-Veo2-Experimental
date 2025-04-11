import { app } from "../../scripts/app.js";

// Register video preview for Veo video nodes
app.registerExtension({
    name: "ComfyUI.Veo2.Extension",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "VeoVideoPreview") {
            // Add custom output display for video preview
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // Create container for video display
                const container = document.createElement("div");
                container.style.width = "100%";
                container.style.height = "auto";
                container.style.overflow = "hidden";
                container.style.display = "flex";
                container.style.flexDirection = "column";
                container.style.alignItems = "center";
                container.style.padding = "10px";
                container.id = "veo-video-container-" + this.id;
                this.videoContainer = container;
                
                // Add container to node's DOM element
                this.widgets_start.parentElement.insertBefore(container, this.widgets_start);
                
                return result;
            };
            
            // Handle displaying generated videos
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                const result = onExecuted ? onExecuted.apply(this, arguments) : undefined;
                
                if (message && message.videos) {
                    // Clear previous videos
                    this.videoContainer.innerHTML = "";
                    
                    // Add each video with controls
                    message.videos.forEach(videoPath => {
                        const videoEl = document.createElement("video");
                        videoEl.src = videoPath.includes("/") ? videoPath : `/view?filename=${videoPath}&type=veo`;
                        videoEl.controls = true;
                        videoEl.autoplay = false;
                        videoEl.loop = true;
                        videoEl.style.width = "100%";
                        videoEl.style.marginBottom = "10px";
                        videoEl.style.borderRadius = "4px";
                        videoEl.style.maxHeight = "400px";
                        
                        this.videoContainer.appendChild(videoEl);
                    });
                }
                
                return result;
            };
        }
    }
});