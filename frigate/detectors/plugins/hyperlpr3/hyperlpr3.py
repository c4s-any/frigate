import onnxruntime as ort
import numpy as np
from frigate.detectors.plugins.hyperlpr3.config.settings import onnx_runtime_config as ort_cfg
from frigate.detectors.plugins.hyperlpr3.inference.pipeline import LPRMultiTaskPipeline
from frigate.detectors.plugins.hyperlpr3.common.typedef import *
from os.path import join
from frigate.detectors.plugins.hyperlpr3.config.settings import _DEFAULT_FOLDER_, get_threads_num
from frigate.detectors.plugins.hyperlpr3.config.configuration import initialization

initialization()

from frigate.detectors.plugins.hyperlpr3.model import MultiTaskDetectorORT, PPRCNNRecognitionORT, ClassificationORT

class LicensePlateCatcher(object):
    def __init__(self,
                 folder: str = _DEFAULT_FOLDER_,
                 detect_level: int = DETECT_LEVEL_LOW,
                 logger_level: int = 3):
        ort.set_default_logger_severity(logger_level)
        
        # 在初始化时获取线程数，避免循环导入
        threads_num = get_threads_num()

        if detect_level == DETECT_LEVEL_LOW:
            # print(join(folder, ort_cfg['det_model_path_320x']))
            det = MultiTaskDetectorORT(threads_num, join(folder, ort_cfg['det_model_path_320x']), input_size=(320, 320))
        elif detect_level == DETECT_LEVEL_HIGH:
            det = MultiTaskDetectorORT(threads_num, join(folder, ort_cfg['det_model_path_640x']), input_size=(640, 640))
        else:
            raise NotImplemented
        rec = PPRCNNRecognitionORT(threads_num, join(folder, ort_cfg['rec_model_path']), input_size=(48, 160))
        cls = ClassificationORT(threads_num, join(folder, ort_cfg['cls_model_path']), input_size=(96, 96))
        self.pipeline = LPRMultiTaskPipeline(detector=det, recognizer=rec, classifier=cls)
    
    def __call__(self, image: np.ndarray, *args, **kwargs):
        return self.pipeline(image)