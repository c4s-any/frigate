"""Creates a go2rtc config file."""

import json
import os
import yaml


BTBN_PATH = "/usr/lib/btbn-ffmpeg"
config_file = os.environ.get("CONFIG_FILE", "/config/config.yml")

# Check if we can use .yaml instead of .yml
config_file_yaml = config_file.replace(".yml", ".yaml")
if os.path.isfile(config_file_yaml):
    config_file = config_file_yaml

with open(config_file) as f:
    raw_config = f.read()

if config_file.endswith((".yaml", ".yml")):
    config = yaml.safe_load(raw_config)
elif config_file.endswith(".json"):
    config = json.loads(raw_config)

go2rtc_config: dict[str, any] = config.get("go2rtc", {})

# we want to ensure that logs are easy to read
if go2rtc_config.get("log") is None:
    go2rtc_config["log"] = {"format": "text"}
elif go2rtc_config["log"].get("format") is None:
    go2rtc_config["log"]["format"] = "text"

if not go2rtc_config.get("webrtc", {}).get("candidates", []):
    default_candidates = []
    # use internal candidate if it was discovered when running through the add-on
    internal_candidate = os.environ.get("FRIGATE_GO2RTC_WEBRTC_CANDIDATE_INTERNAL", None)
    if internal_candidate is not None:
        default_candidates.append(internal_candidate)
    # should set default stun server so webrtc can work
    default_candidates.append("stun:8555")

    go2rtc_config["webrtc"] = {"candidates": default_candidates}

# need to replace ffmpeg command when using ffmpeg4
if not os.path.exists(BTBN_PATH):
    if go2rtc_config.get("ffmpeg") is None:
        go2rtc_config["ffmpeg"] = {
            "rtsp": "-fflags nobuffer -flags low_delay -stimeout 5000000 -user_agent go2rtc/ffmpeg -rtsp_transport tcp -i {input}"
        }
    elif go2rtc_config["ffmpeg"].get("rtsp") is None:
        go2rtc_config["ffmpeg"][
            "rtsp"
        ] = "-fflags nobuffer -flags low_delay -stimeout 5000000 -user_agent go2rtc/ffmpeg -rtsp_transport tcp -i {input}"

print(json.dumps(go2rtc_config))
