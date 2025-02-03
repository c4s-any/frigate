<p align="center">
  <img align="center" alt="logo" src="https://github.com/blakeblackshear/frigate/blob/dev/docs/static/img/frigate.png">
</p>

# 具有本地实时目标检测、人/车特征识别和语义搜索功能的 NVR
## NVR with realtime local object detection, person/vehicle ReID and semantic search 

以 Blake Blackshear 的 [Frigate](https://github.com/blakeblackshear/frigate.git) v0.15.0-beta2 为基础，用 [hyperlpr3](https://github.com/szad670401/HyperLPR) 做车牌识别（仅限中国），参考 [Rethinking_of_PAR](https://github.com/valencebond/Rethinking_of_PAR.git) 自制数据集训练人/车 ReID 模型，用于识别人/车特征。<br>
Based on Blake Blackshear's [Frigate](https://github.com/blakeblackshear/frigate.git) v0.15.0-beta2, use [hyperlpr3](https://github.com/szad670401/HyperLPR) for license plate recognition (China only), and refer to [Rethinking_of_PAR](https://github.com/valencebond/Rethinking_of_PAR.git) to train a person/car ReID model with specialized datasets for identifying person/car features.

最后整合成了一个**专为 [Home Assistant](https://www.home-assistant.io) 设计具有本地实时目标检测、人/车特征识别和语义搜索功能的完整 NVR**。 <br>
Finally, It grew into **a complete NVR designed for [Home Assistant](https://www.home-assistant.io) with funtions of realtime object detection locally, person/vehicle ReID and Semantic Search**.

使用 Google Coral Accelerator 是可选的，但强烈建议使用。CPU 检测只能用于测试目的。Coral 的性能甚至优于最好的 CPU，且能以很少的开销处理 100+ FPS。<br>
Use of a [Google Coral Accelerator](https://coral.ai/products/) is optional, but highly recommended. The Coral will outperform even the best CPUs and can process 100+ FPS with very little overhead.

- 通过定制组件与 Home Assistant 紧密集成。<br>
Tight integration with Home Assistant via a [custom component](https://github.com/blakeblackshear/frigate-hass-integration).

- 旨在通过仅在需要的时间和地点查找目标来最大程度地**减少资源使用**，并最大限度地**提高性能**。<br>
Designed to **minimize resource use and maximize performance** by only looking for objects when and where it is necessary.

- 充分利用多进程，强调**实时性**而不是处理每一帧。<br>
Leverages multiprocessing heavily with an emphasis on **realtime** over processing every frame.

- 使用非常**低开销**的动态侦测来确定在何处运行目标检测。<br>
Uses a very **low overhead** motion detection to determine where to run object detection.

- 目标检测在**单独的进程**中运行，以实现最大FPS。<br>
Object detection runs in **separate processes** for maximum FPS.

- 在抓取不到人脸和车牌的情况下，**ReID** 可以从抓拍**目标**中提取出有效的**特征**（车型、颜色、衣着、年龄段等）。<br>
When the face and license plate cannot be captured, **ReID** can extract effective **features** (model, color, clothing, age, etc.) from the captured **target**.

- **语义搜索**功能允许您通过图像本身、用户定义的文本描述或自动生成的描述来查找您的跟踪目标。<br>
**Semantic Search** allows you to find tracked objects using either the image itself, a user-defined text description, or an automatically generated one. 

- **生成式 AI** 可用于根据跟踪目标的缩略图自动生成描述性文本。这有助于在 Frigate 中进行语义搜索，为您的跟踪目标提供更多上下文信息。<br>
**Generative AI** can be used to automatically generate descriptive text based on the thumbnails of your tracked objects. This helps with Semantic Search in Frigate to provide more context about your tracked objects. 

- 通过 **MQTT** 进行通信，以便轻松集成到其他系统。<br>
Communicates over **MQTT** for easy integration into other systems.

- 基于检测到的目标进行录像存储。<br>
Records video with retention settings based on detected objects.

- 24/7 录像。<br>
24/7 recording.
  
- 通过 RTSP 重新串流以减少与摄像机的连接数。<br>
Re-streaming via RTSP to reduce the number of connections to your camera.

- 支持 WebRTC 和 MSE，可实现低延迟实时查看。<br>
WebRTC & MSE support for low-latency live view.

## 文档（Documentation）

请访问 [https://c4s.tech/docs/](https://c4s.tech/docs/) 查看文档<br>
View the documentation at [https://c4s.tech/docs/](https://c4s.tech/docs/)

## 模型（Model）

人/车 ReID、YOLO-NAS、Yolov7-tiny 和 MobileDet 模型已经测试可用，这些模型都是个人训练的。我在代码中添加了注册和解密的模块，用以保护加密的模型，但不影响非加密的模型使用。<br>
The person/vehicle ReID, YOLO-NAS, Yolov7-tiny and MobileDet models are also already available, which are all personally trained. I have added modules for registration and decryption to the code to protect the encrypted models. However, it does not affect the use of non-encrypted models.

人/车 ReID 使用 ONNX 检测器进行模型推理，支持 30 多种行人特征、多种车辆特征、400多种车型。<br>
Person/Vehicle ReID uses ONNX detector for model inference, supporting more than 30 pedestrian features, multiple vehicle features, and more than 400 vehicle models.

## 增加的部分

相比原始Frigate增加了人车特征识别、车牌识别（仅限中国），前端UI已经汉化为简体中文。车牌识别是将[hyperlpr3](https://github.com/szad670401/HyperLPR)代码和模型加了进来，运行时不需要再拉取，主要是在中国很难下载，另外make构建时pip源更换成了清华的，有利于中国的用户可以加速构建镜像。我已经成功测试构建x86镜像（英伟达和Coral Edgetpu）并正常运行，没有测试arm64平台（因为手上没有相关硬件设备）。<br>
Compared with the original Frigate, it adds human-vehicle attribute recognition, license plate recognition (China only), and the front-end UI has been simplified into Simplified Chinese. License plate recognition is the [hyperlpr3](https://github.com/szad670401/HyperLPR) code and model added in, runtime does not need to pull again, mainly in China is difficult to download, in addition to make build pip source replaced with Tsinghua source, in favor of Chinese users can accelerate the build image. I've successfully tested building x86 images (nVidia and Coral edgetpu) and running them properly, not testing the arm64 platform (as I don't have the relevant hardware devices on hand).

## 截图（Screenshots）

### 实时看板（Live dashboard）
<div>
<img width="800" alt="Live dashboard" src="https://c4s.tech/img/printscreen01_1.jpg">
</div>

### 行人特征识别（Person ReID）
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen06_1.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen07_1.jpg">
</div>

### 机动车特征识别（Vehicle ReID）
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen04_2.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen05_2.jpg">
</div>

### 内置遮罩和防区编辑器（Built-in mask and zone editor）
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen08.jpg">
</div>

<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen09.jpg">
</div>

### 多摄像机警报消除（Multi-camera scrubbing）
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen02_1.jpg">
</div>
