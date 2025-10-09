<p align="center">
  <img align="center" alt="logo" src="https://github.com/blakeblackshear/frigate/blob/dev/docs/static/img/frigate.png">
</p>

# 具有本地实时目标检测、人/车特征识别和语义搜索功能的 NVR

<p align="center"><a href="https://github.com/c4s-any/frigate/blob/dev/README_CN.md">中文</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/c4s-any/frigate/blob/dev/README.md">EN</a></p>

以 Blake Blackshear 的 [Frigate](https://github.com/blakeblackshear/frigate.git) 为基础，用 [hyperlpr3](https://github.com/szad670401/HyperLPR) 做中国车牌识别，并保留了原来的 Paddle 车牌识别以支持其它国家和地区，参考 [Rethinking_of_PAR](https://github.com/valencebond/Rethinking_of_PAR.git) 自制数据集训练人/车 ReID 模型，用于识别人/车特征。

最后整合成了一个**可于 [Home Assistant](https://www.home-assistant.io) 集成具有本地实时目标检测、人/车特征识别和语义搜索功能的完整 NVR**。 

使用 [Google Coral Accelerator](https://coral.ai/products/) 是可选的，但强烈建议使用。CPU 检测只能用于测试目的。Coral 的性能甚至优于最好的 CPU，且能以很少的开销处理 100+ FPS。

- 通过[定制组件](https://github.com/blakeblackshear/frigate-hass-integration)与 Home Assistant 紧密集成。

- 旨在通过仅在需要的时间和地点查找目标来最大程度地**减少资源使用**，并最大限度地**提高性能**。

- 充分利用多进程，强调**实时性**而不是处理每一帧。

- 使用非常**低开销**的动态侦测来确定在何处运行目标检测。

- 目标检测在**单独的进程**中运行，以实现最大FPS。

- 在抓取不到人脸和车牌的情况下，**ReID** 可以从抓拍**目标**中提取出有效的**特征**（车型、颜色、衣着、年龄段等）。

- **语义搜索**功能允许您通过图像本身、用户定义的文本描述或自动生成的描述来查找您的跟踪目标。

- **生成式 AI** 可用于根据跟踪目标的缩略图自动生成描述性文本。这有助于在 Frigate 中进行语义搜索，为您的跟踪目标提供更多上下文信息。 

- 通过 **MQTT** 进行通信，以便轻松集成到其他系统。

- 基于检测到的目标进行录像存储。

- 24/7 录像。
  
- 通过 RTSP 重新串流以减少与摄像机的连接数。

- 支持 WebRTC 和 MSE，可实现低延迟实时查看。

## 文档

请访问 [https://c4s.tech/docs/](https://c4s.tech/docs/) 查看文档。

## 模型

人/车 ReID 和 YOLO-NAS 模型已经测试可用，这些模型都是个人训练的。

人/车 ReID 使用 ONNX 检测器进行模型推理，支持 30 多种行人特征、多种车辆特征、400多种车型。

这些模型是加密模型，需要的可以联系我，但不妨碍使用您自己的模型。


## 增加的部分

相比原始 Frigate 增加了人/车特征识别、中国车牌识别，中文前端UI文本矫正。车牌识别是将 [hyperlpr3](https://github.com/szad670401/HyperLPR) 代码和模型加了进来，运行时不需要再拉取。修改了部分代码，使人/车特征可以被当作子标签进行查找筛选。已经成功测试构建x86镜像（nvidia和 Coral Edgetpu ）并正常运行，没有测试arm64平台（因为手上没有相关硬件设备）。

## 截图

### 实时看板
<div>
<img width="800" alt="Live dashboard" src="https://c4s.tech/img/printscreen01_1.jpg">
</div>

### 行人特征识别
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen06_1.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen07_1.jpg">
</div>

### 机动车特征识别
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen04_2.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen05_2.jpg">
</div>

### 内置遮罩和防区编辑器
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen08.jpg">
</div>

<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen09.jpg">
</div>

### 多摄像机警报消除
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen02_1.jpg">
</div>
