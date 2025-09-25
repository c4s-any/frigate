import logging

from frigate.embeddings.onnx.lpr_embedding import (
    LicensePlateDetector,
    PaddleOCRClassification,
    PaddleOCRDetection,
    PaddleOCRRecognition,
)
from frigate.embeddings.hyperlpr.hyperlpr_embedding import HyperLPRModelRunner

from ...types import DataProcessorModelRunner

logger = logging.getLogger(__name__)


class LicensePlateModelRunner(DataProcessorModelRunner):
    def __init__(self, requestor, device: str = "CPU", model_size: str = "small", use_hyperlpr: bool = False):
        super().__init__(requestor, device, model_size)
        self.use_hyperlpr = use_hyperlpr
        
        if use_hyperlpr:
            try:
                # Try to use HyperLPR for license plate recognition
                self.hyperlpr_model = HyperLPRModelRunner(
                    model_size=model_size, requestor=requestor, device=device
                )
                self.hyperlpr_model._load_model_and_utils()
                logger.info("HyperLPR3 initialized successfully - using HyperLPR for license plate recognition")
            except Exception as e:
                logger.warning(f"Failed to initialize HyperLPR3: {e}. Falling back to PaddleOCR.")
                self.use_hyperlpr = False
                # Fallback to PaddleOCR
                self._initialize_paddleocr_models(requestor, device, model_size)
        else:
            # Use original PaddleOCR + YOLOv9 models
            self._initialize_paddleocr_models(requestor, device, model_size)
    
    def _initialize_paddleocr_models(self, requestor, device: str, model_size: str):
        """Initialize PaddleOCR models as fallback."""
        self.detection_model = PaddleOCRDetection(
            model_size=model_size, requestor=requestor, device=device
        )
        self.classification_model = PaddleOCRClassification(
            model_size=model_size, requestor=requestor, device=device
        )
        self.recognition_model = PaddleOCRRecognition(
            model_size=model_size, requestor=requestor, device=device
        )
        self.yolov9_detection_model = LicensePlateDetector(
            model_size=model_size, requestor=requestor, device=device
        )

        # Load all models once
        self.detection_model._load_model_and_utils()
        self.classification_model._load_model_and_utils()
        self.recognition_model._load_model_and_utils()
        self.yolov9_detection_model._load_model_and_utils()
        logger.info("PaddleOCR models initialized successfully")
