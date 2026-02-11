import json
import numpy as np
from PIL import Image, ImageFilter
from JARVIS.core.hardware.profile import detect_hardware

class AdaptiveVisionPipeline:
    """
    Implements the "Saccadic Vision" approach.
    Real implementation using Pillow/Numpy for Saliency Detection.
    """

    def __init__(self, hardware_profile):
        self.hardware = hardware_profile

    def scan_low_res(self, image_path: str):
        """
        Step 1: Low-Res Scan & Saliency Detection.

        ALGORITHM:
        1. Resize to (360, 360).
        2. Convert to Grayscale.
        3. Apply Edge Detection (Finds text/shapes).
        4. Calculate Variance in 4 quadrants.
        5. Return the quadrant with highest variance (most info).
        """
        try:
            with Image.open(image_path) as img:
                # 1. Resize
                low_res = img.resize((360, 360))
                # 2. Grayscale
                gray = low_res.convert("L")
                # 3. Edge Detection (Simple Saliency)
                edges = gray.filter(ImageFilter.FIND_EDGES)

                # 4. Quadrant Analysis (Numpy)
                arr = np.array(edges)
                h, w = arr.shape
                mid_h, mid_w = h // 2, w // 2

                quadrants = [
                    (arr[0:mid_h, 0:mid_w], [0, 0, mid_w, mid_h]),       # Top-Left
                    (arr[0:mid_h, mid_w:w], [mid_w, 0, w, mid_h]),       # Top-Right
                    (arr[mid_h:h, 0:mid_w], [0, mid_h, mid_w, h]),       # Bottom-Left
                    (arr[mid_h:h, mid_w:w], [mid_w, mid_h, w, h])        # Bottom-Right
                ]

                best_q = None
                max_var = -1

                for q_arr, bbox in quadrants:
                    var = np.var(q_arr) # Variance = Information Density
                    if var > max_var:
                        max_var = var
                        best_q = bbox

                # Scale bbox back to original size?
                # For this demo, we return the relative 360p bbox and score
                return [{"bbox": best_q, "score": float(max_var), "ref_size": (360, 360)}]
        except Exception as e:
            print(f"Vision Error: {e}")
            return []

    def crop_roi(self, image_path: str, bbox, ref_size):
        """
        Step 2: Attention Filter (Cropping).
        """
        try:
            with Image.open(image_path) as img:
                w, h = img.size
                ref_w, ref_h = ref_size

                # Scale bbox to original resolution
                scale_x = w / ref_w
                scale_y = h / ref_h

                x1, y1, x2, y2 = bbox
                real_bbox = (
                    int(x1 * scale_x),
                    int(y1 * scale_y),
                    int(x2 * scale_x),
                    int(y2 * scale_y)
                )

                return img.crop(real_bbox)
        except Exception:
            return None

    def process_high_res(self, cropped_image):
        """
        Step 3: Foveal Zoom (Heavy Compute).
        """
        # In a real system, this goes to OCR.
        # Here we return metadata to prove we have the crop.
        if cropped_image:
            return f"Analyzed Crop: Size {cropped_image.size}. High Variance Region detected."
        return "Analysis Failed."

    def execute(self, image_path: str):
        # 1. Hardware Check
        if self.hardware.overall_score < 50:
            return "Hardware too weak."

        # 2. Pipeline
        rois = self.scan_low_res(image_path)
        results = []

        for roi in rois:
            # Dynamic Threshold based on image noise?
            # For now, just take the best one
            crop = self.crop_roi(image_path, roi['bbox'], roi['ref_size'])
            analysis = self.process_high_res(crop)
            results.append(analysis)

        return "\n".join(results)

class VisionPlugin:
    def __init__(self):
        self.profile = detect_hardware()
        self.pipeline = AdaptiveVisionPipeline(self.profile)

    def analyze_image(self, image_path: str):
        return self.pipeline.execute(image_path)
