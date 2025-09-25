"""HyperLPR integration for license plate recognition."""

import logging
from typing import List, Tuple, Optional
import numpy as np
import cv2

try:
    from frigate.detectors.plugins.hyperlpr3.hyperlpr3 import LicensePlateCatcher
    from frigate.detectors.plugins.hyperlpr3.common.typedef import DETECT_LEVEL_LOW, DETECT_LEVEL_HIGH
except ImportError:
    LicensePlateCatcher = None

from ...data_processing.types import DataProcessorModelRunner

logger = logging.getLogger(__name__)


class HyperLPRModelRunner(DataProcessorModelRunner):
    """HyperLPR model runner for license plate recognition."""
    
    def __init__(self, requestor, device: str = "CPU", model_size: str = "small"):
        super().__init__(requestor, device, model_size)
        
        if LicensePlateCatcher is None:
            raise ImportError("HyperLPR3 is not installed. Please install hyperlpr3 package.")
        
        # Initialize LicensePlateCatcher with optimized configuration for Chinese license plates
        try:
            # Determine detection level based on model size
            detect_level = DETECT_LEVEL_HIGH if model_size == "large" else DETECT_LEVEL_LOW
            
            # Initialize the license plate catcher
            self.hyperlpr = LicensePlateCatcher(
                detect_level=detect_level,
                logger_level=3  # Set appropriate log level
            )
            logger.info(f"HyperLPR3 initialized with detection level: {detect_level}")
        except Exception as e:
            logger.error(f"Failed to initialize HyperLPR3: {e}")
            raise
    
    def _load_model_and_utils(self):
        """Load the HyperLPR model and utilities."""
        # HyperLPR3 models are loaded automatically on initialization
        logger.info("HyperLPR3 model loaded successfully")
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better Chinese license plate recognition.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply histogram equalization for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Convert back to 3-channel if original was 3-channel
        if len(image.shape) == 3:
            return cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
        else:
            return blurred

    def detect_and_recognize(self, image: np.ndarray) -> List[Tuple[str, float, Tuple[int, int, int, int]]]:
        """
        Detect and recognize license plates in the image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of tuples containing (plate_text, confidence, bbox)
            where bbox is (x1, y1, x2, y2)
        """
        try:
            # Preprocess image for better Chinese character recognition
            processed_image = self._preprocess_image(image)
            
            # Run HyperLPR3 detection and recognition
            results = self.hyperlpr(processed_image)
            
            plates = []
            for result in results:
                # New format: [plate_code, rec_confidence, plate_type, det_bound_box]
                plate_text = result[0]  # License plate text
                confidence = result[1]  # Recognition confidence score
                plate_type = result[2]  # Plate type (not used in this context)
                bbox = result[3]  # Bounding box coordinates [x1, y1, x2, y2]
                
                # Ensure proper encoding for Chinese characters
                if isinstance(plate_text, bytes):
                    try:
                        plate_text = plate_text.decode('utf-8')
                    except UnicodeDecodeError:
                        plate_text = plate_text.decode('gbk', errors='ignore')
                
                # Convert bbox format if needed
                if len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                else:
                    # Handle different bbox formats
                    x1, y1, w, h = bbox
                    x2, y2 = x1 + w, y1 + h
                
                plates.append((plate_text, confidence, (int(x1), int(y1), int(x2), int(y2))))
            
            return plates
            
        except Exception as e:
            logger.error(f"Error in HyperLPR detection: {e}")
            return []
    
    def recognize_only(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """
        Recognize license plate text from a cropped license plate image.
        
        Args:
            image: Cropped license plate image
            
        Returns:
            List of tuples containing (plate_text, confidence)
        """
        try:
            # Preprocess image for better Chinese character recognition
            processed_image = self._preprocess_image(image)
            
            # For cropped images, we still use the full detection pipeline
            # but expect only one result
            results = self.hyperlpr(processed_image)
            
            if results:
                # New format: [plate_code, rec_confidence, plate_type, det_bound_box]
                plate_text = results[0][0]
                confidence = results[0][1]
                
                # Ensure proper encoding for Chinese characters
                if isinstance(plate_text, bytes):
                    try:
                        plate_text = plate_text.decode('utf-8')
                    except UnicodeDecodeError:
                        plate_text = plate_text.decode('gbk', errors='ignore')
                
                return [(plate_text, confidence)]
            
            return []
            
        except Exception as e:
            logger.error(f"Error in HyperLPR recognition: {e}")
            return []


