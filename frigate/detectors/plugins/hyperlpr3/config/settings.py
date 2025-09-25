import os
import sys
from frigate.const import LPR_PATH

# 延迟加载配置以避免循环导入
def get_threads_num():
    try:
        from frigate.config.config import FrigateConfig
        config = FrigateConfig.load(install=True)
        return config.hyperlpr.thread_num
    except Exception:
        return 2  # 默认值

# 不在模块导入时调用，而是在需要时调用
THREADS_NUM = 2  # 默认值

_MODEL_VERSION_ = "20230229"

if 'win32' in sys.platform:
    #_DEFAULT_FOLDER_ = os.path.join(os.environ['HOMEPATH'], ".hyperlpr3")
    _DEFAULT_FOLDER_ = LPR_PATH
else:
    #_DEFAULT_FOLDER_ = os.path.join(os.environ['HOME'], ".hyperlpr3")
    _DEFAULT_FOLDER_ = LPR_PATH

_ONLINE_URL_ = "http://hyperlpr.tunm.top/raw/"

onnx_runtime_config = dict(
    det_model_path_320x=os.path.join(_MODEL_VERSION_, "onnx", "y5fu_320x_sim.onnx"),
    det_model_path_640x=os.path.join(_MODEL_VERSION_, "onnx", "y5fu_640x_sim.onnx"),
    rec_model_path=os.path.join(_MODEL_VERSION_, "onnx", "rpv3_mdict_160_r3.onnx"),
    cls_model_path=os.path.join(_MODEL_VERSION_, "onnx", "litemodel_cls_96x_r1.onnx"),
)

onnx_model_maps = ["det_model_path_320x", "det_model_path_640x", "rec_model_path", "cls_model_path"]

_REMOTE_URL_ = "https://github.com/szad670401/HyperLPR/blob/master/resource/models/onnx/"
