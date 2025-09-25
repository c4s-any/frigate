import logging
import copy
import math

import cv2
import numpy as np

from frigate.detectors.plugins.hyperlpr3.inference.base.base import HamburgerABC
from frigate.detectors.plugins.hyperlpr3.common.tokenize import token

from frigate.detectors.plugins.hyperlpr3.engine_factory import InferenceEngine

logger = logging.getLogger(__name__)

# <-- MultiTaskDetector
def xywh2xyxy(boxes):
    xywh = copy.deepcopy(boxes)
    xywh[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xywh[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xywh[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xywh[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    return xywh


def nms(boxes, iou_thresh):  # nms
    index = np.argsort(boxes[:, 4])[::-1]
    keep = []
    while index.size > 0:
        i = index[0]
        keep.append(i)
        x1 = np.maximum(boxes[i, 0], boxes[index[1:], 0])
        y1 = np.maximum(boxes[i, 1], boxes[index[1:], 1])
        x2 = np.minimum(boxes[i, 2], boxes[index[1:], 2])
        y2 = np.minimum(boxes[i, 3], boxes[index[1:], 3])

        w = np.maximum(0, x2 - x1)
        h = np.maximum(0, y2 - y1)

        inter_area = w * h
        union_area = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1]) + (
                boxes[index[1:], 2] - boxes[index[1:], 0]) * (boxes[index[1:], 3] - boxes[index[1:], 1])
        iou = inter_area / (union_area - inter_area)
        idx = np.where(iou <= iou_thresh)[0]
        index = index[idx + 1]
    return keep


def restore_box(boxes, r, left, top):
    boxes[:, [0, 2, 5, 7, 9, 11]] -= left
    boxes[:, [1, 3, 6, 8, 10, 12]] -= top

    boxes[:, [0, 2, 5, 7, 9, 11]] /= r
    boxes[:, [1, 3, 6, 8, 10, 12]] /= r
    return boxes


def detect_pre_precessing(img, img_size):
    img, r, left, top = letter_box(img, img_size)
    img = img[:, :, ::-1].transpose(2, 0, 1).copy().astype(np.float32)
    img = img / 255
    img = img.reshape(1, *img.shape)
    return img, r, left, top


def post_precessing(dets, r, left, top, conf_thresh=0.25, iou_thresh=0.5):
    choice = dets[:, :, 4] > conf_thresh
    dets = dets[choice]
    dets[:, 13:15] *= dets[:, 4:5]
    box = dets[:, :4]
    boxes = xywh2xyxy(box)
    score = np.max(dets[:, 13:15], axis=-1, keepdims=True)
    index = np.argmax(dets[:, 13:15], axis=-1).reshape(-1, 1)
    output = np.concatenate((boxes, score, dets[:, 5:13], index), axis=1)
    reserve_ = nms(output, iou_thresh)
    output = output[reserve_]
    output = restore_box(output, r, left, top)
    return output


def letter_box(img, size=(640, 640)):
    h, w, c = img.shape
    r = min(size[0] / h, size[1] / w)
    new_h, new_w = int(h * r), int(w * r)
    top = int((size[0] - new_h) / 2)
    left = int((size[1] - new_w) / 2)

    bottom = size[0] - new_h - top
    right = size[1] - new_w - left
    img_resize = cv2.resize(img, (new_w, new_h))
    img = cv2.copyMakeBorder(img_resize, top, bottom, left, right, borderType=cv2.BORDER_CONSTANT,
                             value=(0, 0, 0))
    return img, r, left, top
# MultiTaskDetector-->

# <--recognition
def encode_images(image: np.ndarray, max_wh_ratio, target_shape, limited_max_width=160, limited_min_width=48):
    imgC = 3
    imgH, imgW = target_shape
    # cv2.imshow("image", image)
    # cv2.waitKey(0)
    assert imgC == image.shape[2]
    max_wh_ratio = max(max_wh_ratio, imgW / imgH)
    imgW = int((imgH * max_wh_ratio))
    imgW = max(min(imgW, limited_max_width), limited_min_width)
    h, w = image.shape[:2]
    ratio = w / float(h)
    ratio_imgH = math.ceil(imgH * ratio)
    ratio_imgH = max(ratio_imgH, limited_min_width)
    if ratio_imgH > imgW:
        resized_w = imgW
    else:
        resized_w = int(ratio_imgH)
    resized_image = cv2.resize(image, (resized_w, imgH))
    # print((resized_w, imgH))
    # padding_im1 = np.ones((imgH, imgW, imgC), dtype=np.uint8) * 128
    # padding_im1[:, 0:resized_w, :] = resized_image
    # cv2.imwrite("pad.jpg", padding_im1)

    resized_image = resized_image.astype('float32')
    resized_image = (resized_image.transpose((2, 0, 1)) - 127.5) / 127.5
    # resized_image -= 0.5
    # resized_image *= 2
    padding_im = np.zeros((imgC, imgH, imgW), dtype=np.float32)
    padding_im[:, :, 0:resized_w] = resized_image

    # np.save('fk.npy', padding_im)

    return padding_im

def get_ignored_tokens():
    return [0]  # for ctc blank
# recognition-->

# <-- classification
def encode_images_classification(image: np.ndarray):
    image_encode = image / 255.0
    if len(image_encode.shape) == 4:
        image_encode = image_encode.transpose(0, 3, 1, 2)
    else:
        image_encode = image_encode.transpose(2, 0, 1)
    image_encode = image_encode.astype(np.float32)

    return image_encode
# classification -- >

class MultiTaskDetectorORT(HamburgerABC):

    def __init__(self, thread_num: int, onnx_path, box_threshold: float = 0.5, nms_threshold: float = 0.6, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.box_threshold = box_threshold
        self.nms_threshold = nms_threshold

        self.engine = InferenceEngine(onnx_path, thread_num)
        self.session = self.engine.session
        if self.engine.engine_type == "openvino":
            # Get input and output information
            self.inputs_option = self.session.inputs
            self.outputs_option = self.session.outputs
            input_option = self.inputs_option[0]
            input_size_ = tuple(input_option.shape[2:])
            if not hasattr(self, 'input_size'):
                self.input_size = input_size_
            else:
                assert self.input_size == input_size_, 'The dimensions of the input do not match the model expectations.'
            assert self.input_size[0] == self.input_size[1]
            self.input_name = input_option.get_any_name()  # OpenVINO uses get_any_name() for input names
        else:
            # Get input and output information
            self.inputs_option = self.session.get_inputs()
            self.outputs_option = self.session.get_outputs()
            input_option = self.inputs_option[0]
            input_size_ = tuple(input_option.shape[2:])
            self.input_size = tuple(self.input_size)
            if not self.input_size:
                self.input_size = input_size_
            assert self.input_size == input_size_, 'The dimensions of the input do not match the model expectations.'
            assert self.input_size[0] == self.input_size[1]
            self.input_name = input_option.name

    def _run_session(self, data):
        #result = self.session.run([self.outputs_option[0].name], {self.input_name: data})[0]
        if self.engine.engine_type == "openvino":
            # OpenVINO 推理
            infer_request = self.session.create_infer_request()
            results = infer_request.infer({self.input_name: data})
            
            # 获取第一个输出（假设模型只有一个输出）
            output_tensor = next(iter(results.values()))
            return output_tensor
        else:
            # ONNX Runtime 推理方式
            result = self.session.run(
                [self.outputs_option[0].name], 
                {self.input_name: data}
            )[0]
            
        return result

    def _postprocess(self, data):
        r, left, top = self.tmp_pack
        return post_precessing(data, r, left, top)

    def _preprocess(self, image):
        img, r, left, top = detect_pre_precessing(image, self.input_size)
        self.tmp_pack = r, left, top

        return img

class PPRCNNRecognitionORT(HamburgerABC):

    def __init__(self, thread_num: int, onnx_path, token_dict=token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.character_list = token_dict

        self.engine = InferenceEngine(onnx_path, thread_num)
        self.session = self.engine.session
        if self.engine.engine_type == "openvino":
            self.input_config = self.session.inputs[0]
            self.output_config = self.session.outputs[0]
            self.input_size = tuple(self.input_config.shape[2:])
        else:
            self.input_config = self.session.get_inputs()[0]
            self.output_config = self.session.get_outputs()[0]
            self.input_size = tuple(self.input_config.shape[2:])

    def decode(self, text_index, text_prob=None, is_remove_duplicate=False):
        """ convert text-index into text-label. """
        result_list = []
        ignored_tokens = get_ignored_tokens()
        batch_size = len(text_index)
        for batch_idx in range(batch_size):
            char_list = []
            conf_list = []
            for idx in range(len(text_index[batch_idx])):
                if text_index[batch_idx][idx] in ignored_tokens:
                    continue
                if is_remove_duplicate:
                    # only for predict
                    if idx > 0 and text_index[batch_idx][idx - 1] == text_index[batch_idx][idx]:
                        continue
                # print(int(text_index[batch_idx][idx]))
                char_list.append(self.character_list[int(text_index[batch_idx][idx])])
                if text_prob is not None:
                    conf_list.append(text_prob[batch_idx][idx])
                else:
                    conf_list.append(1)
            text = ''.join(char_list)
            result_list.append((text, np.mean(conf_list)))
        return result_list

    # @cost("Recognition")
    def _run_session(self, data) -> np.ndarray:
        try:
            if self.engine.engine_type == "openvino":
                # OpenVINO 推理
                result = self.session([data])
                return [output_data for output_data in result.values()]
            else:
                # ONNX Runtime 推理
                result = self.session.run(
                    [self.output_config.name],
                    {self.input_config.name: data}
                )
                
                return result
        except Exception as e:
            logger.error(f"推理失败: {str(e)}")
            raise

    def _postprocess(self, data) -> tuple:
        if data:
            prod = data[0]
            argmax = np.argmax(prod, axis=2)
            rmax = np.max(prod, axis=2)
            result = self.decode(argmax, rmax, is_remove_duplicate=True)

            return result[0]
        else:
            return '', 0.0

    def _preprocess(self, image) -> np.ndarray:
        assert len(
            image.shape) == 3, "The dimensions of the input image object do not match. The input supports a single " \
                               "image. "
        h, w, _ = image.shape
        wh_ratio = w * 1.0 / h
        data = encode_images(image, wh_ratio, self.input_size, )
        data = np.expand_dims(data, 0)
        # print(data.shape)

        return data

class ClassificationORT(HamburgerABC):

    def __init__(self, thread_num: int, onnx_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.engine = InferenceEngine(onnx_path, thread_num)
        self.session = self.engine.session
        if self.engine.engine_type == "openvino":
            self.input_config = self.session.inputs[0]
            self.output_config = self.session.outputs[0]
            self.input_size = tuple(self.input_config.shape[2:])
        else:
            self.input_config = self.session.get_inputs()[0]
            self.output_config = self.session.get_outputs()[0]
            self.input_size = tuple(self.input_config.shape[2:])

    # @cost('Cls')
    def _run_session(self, data) -> np.ndarray:
        try:
            if self.engine.engine_type == "openvino":
                # OpenVINO 推理
                result = self.session([data])
                return [output_data for output_data in result.values()]
            else:
                # ONNX Runtime 推理
                result = self.session.run([self.output_config.name], {self.input_config.name: data})
                return result[0]
        except Exception as e:
            logger.error(f"推理失败: {str(e)}")
            raise

    def _postprocess(self, data) -> np.ndarray:
        return data

    def _preprocess(self, image) -> np.ndarray:
        assert len(
            image.shape) == 3, "The dimensions of the input image object do not match. The input supports a single " \
                               "image. "
        # print(self.input_size)
        image_resize = cv2.resize(image, self.input_size)
        encode = encode_images_classification(image_resize)
        encode = encode.astype(np.float32)
        input_tensor = np.expand_dims(encode, 0)

        return input_tensor