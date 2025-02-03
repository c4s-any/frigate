import cv2
import numpy as np
from .base.base import HamburgerABC
from hyperlpr3.common.tools_process import cost


def encode_images(image: np.ndarray):
    image_encode = image / 255.0
    if len(image_encode.shape) == 4:
        image_encode = image_encode.transpose(0, 3, 1, 2)
    else:
        image_encode = image_encode.transpose(2, 0, 1)
    image_encode = image_encode.astype(np.float32)

    return image_encode


class ClassificationORT(HamburgerABC):

    def __init__(self, onnx_path, *args, **kwargs):
        import onnxruntime as ort
        super().__init__(*args, **kwargs)
        # new
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
        self.session = ort.InferenceSession(onnx_path, session_options, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], provider_options=[{'device_id': 0}, {}])
        # original
        #self.session = ort.InferenceSession(onnx_path, None)
        self.input_config = self.session.get_inputs()[0]
        self.output_config = self.session.get_outputs()[0]
        self.input_size = tuple(self.input_config.shape[2:])

    # @cost('Cls')
    def _run_session(self, data) -> np.ndarray:
        result = self.session.run([self.output_config.name], {self.input_config.name: data})

        return result[0]

    def _postprocess(self, data) -> np.ndarray:
        return data

    def _preprocess(self, image) -> np.ndarray:
        assert len(
            image.shape) == 3, "The dimensions of the input image object do not match. The input supports a single " \
                               "image. "
        # print(self.input_size)
        image_resize = cv2.resize(image, self.input_size)
        encode = encode_images(image_resize)
        encode = encode.astype(np.float32)
        input_tensor = np.expand_dims(encode, 0)

        return input_tensor


