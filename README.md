<p align="center">
  <img align="center" alt="logo" src="https://github.com/blakeblackshear/frigate/blob/dev/docs/static/img/frigate.png">
</p>

# NVR with realtime local object detection, person/vehicle ReID and semantic search 

<p align="center"><a href="https://github.com/c4s-any/frigate/blob/dev/README.md">EN</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/c4s-any/frigate/blob/dev/README_CN.md">中文</a></p>

Based on Blake Blackshear's [Frigate](https://github.com/blakeblackshear/frigate.git), [hyperlpr3](https://github.com/szad670401/HyperLPR) is used for Chinese license plate recognition, and the original Paddle license plate recognition is retained to support other countries and regions. The person/vehicle ReID model is trained with reference to the self-made [Rethinking_of_PAR](https://github.com/valencebond/Rethinking_of_PAR.git) dataset to identify person/vehicle features.

It eventually grew into **a complete NVR that can be integrated with [Home Assistant](https://www.home-assistant.io) and with funtions of realtime object detection locally, person/vehicle ReID and Semantic Search**.

Use of a [Google Coral Accelerator](https://coral.ai/products/) is optional, but highly recommended. The Coral will outperform even the best CPUs and can process 100+ FPS with very little overhead.

- Tight integration with Home Assistant via a [custom component](https://github.com/blakeblackshear/frigate-hass-integration).

- Designed to **minimize resource use and maximize performance** by only looking for objects when and where it is necessary.

- Leverages multiprocessing heavily with an emphasis on **realtime** over processing every frame.

- Uses a very **low overhead** motion detection to determine where to run object detection.

- Object detection runs in **separate processes** for maximum FPS.

- When the face and license plate cannot be captured, **ReID** can extract effective **features** (model, color, clothing, age, etc.) from the captured **target**.

- **Semantic Search** allows you to find tracked objects using either the image itself, a user-defined text description, or an automatically generated one. 

- **Generative AI** can be used to automatically generate descriptive text based on the thumbnails of your tracked objects. This helps with Semantic Search in Frigate to provide more context about your tracked objects. 

- Communicates over **MQTT** for easy integration into other systems.

- Records video with retention settings based on detected objects.

- 24/7 recording.

- Re-streaming via RTSP to reduce the number of connections to your camera.

- WebRTC & MSE support for low-latency live view.

## Documentation

View the documentation at [https://c4s.tech/docs/](https://c4s.tech/docs/)

## Model

The person/vehicle ReID and YOLO-NAS models are also already available, which are all personally trained.

Person/Vehicle ReID uses ONNX detector for model inference, supporting more than 30 pedestrian features, multiple vehicle features, and more than 400 vehicle models.

These models are encrypted models. If you need them, you can contact me, but it does not prevent you from using your own models.

## Increased part

Compared with the original Frigate, it adds pedestrian/vehicle feature recognition, Chinese license plate recognition, and Chinese front-end UI text correction. License plate recognition is the [hyperlpr3](https://github.com/szad670401/HyperLPR) code and model added in, no need to pull it at runtime. I've successfully tested building x86 images (nVidia and Coral edgetpu) and running them properly, not testing the arm64 platform (as I don't have the relevant hardware devices on hand).

## Screenshots

### Live dashboard
<div>
<img width="800" alt="Live dashboard" src="https://c4s.tech/img/printscreen01_1.jpg">
</div>

### Person ReID
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen06_1.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen07_1.jpg">
</div>

### Vehicle ReID
<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen04_2.jpg">
</div>

<div>
<img width="800" alt="Streamlined review workflow" src="https://c4s.tech/img/printscreen05_2.jpg">
</div>

### Built-in mask and zone editor
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen08.jpg">
</div>

<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen09.jpg">
</div>

### Multi-camera scrubbing
<div>
<img width="800" alt="Built-in mask and zone editor" src="https://c4s.tech/img/printscreen02_1.jpg">
</div>
