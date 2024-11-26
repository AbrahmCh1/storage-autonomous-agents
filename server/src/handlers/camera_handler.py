import base64
import os
from datetime import datetime

class CameraHandler:
    def __init__(self, save_directory="server/captured_images"):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)

    def handle_camera_capture(self, data):
        robot_id = data[0]
        base64_image = data[1]
        
        # Convert base64 to image and save
        image_data = base64.b64decode(base64_image)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.save_directory}/robot_{robot_id}_{timestamp}.png"
        
        with open(filename, "wb") as f:
            f.write(image_data)
        
        print(f"Received and saved image from robot {robot_id}") 