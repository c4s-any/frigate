import onnxruntime as ort
from frigate.detectors.plugins.hyperlpr3.config.settings import onnx_runtime_config as ort_cfg
from frigate.detectors.plugins.hyperlpr3.inference.pipeline import LPRMultiTaskPipeline
from frigate.detectors.plugins.hyperlpr3.common.typedef import *
from os.path import join
from frigate.detectors.plugins.hyperlpr3.config.settings import _DEFAULT_FOLDER_, THREADS_NUM
from frigate.detectors.plugins.hyperlpr3.config.configuration import initialization

initialization()

from frigate.detectors.plugins.hyperlpr3.model import MultiTaskDetectorORT, PPRCNNRecognitionORT, ClassificationORT

class LicensePlateCatcher(object):
    def __init__(self,
                 folder: str = _DEFAULT_FOLDER_,
                 detect_level: int = DETECT_LEVEL_LOW,
                 logger_level: int = 3):
        ort.set_default_logger_severity(logger_level)

        if detect_level == DETECT_LEVEL_LOW:
            # print(join(folder, ort_cfg['det_model_path_320x']))
            det = MultiTaskDetectorORT(THREADS_NUM, join(folder, ort_cfg['det_model_path_320x']), input_size=(320, 320))
        elif detect_level == DETECT_LEVEL_HIGH:
            det = MultiTaskDetectorORT(THREADS_NUM, join(folder, ort_cfg['det_model_path_640x']), input_size=(640, 640))
        else:
            raise NotImplemented
        rec = PPRCNNRecognitionORT(THREADS_NUM, join(folder, ort_cfg['rec_model_path']), input_size=(48, 160))
        cls = ClassificationORT(THREADS_NUM, join(folder, ort_cfg['cls_model_path']), input_size=(96, 96))
        self.pipeline = LPRMultiTaskPipeline(detector=det, recognizer=rec, classifier=cls)
    
    def __call__(self, image: np.ndarray, *args, **kwargs):
        return self.pipeline(image)