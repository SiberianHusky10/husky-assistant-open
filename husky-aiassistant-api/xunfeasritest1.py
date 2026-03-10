import os
import pyaudio
from dotenv import load_dotenv
from xfyunsdkspeech.rtasr_client import RtasrClient

# 加载 .env（RTASR_ID / RTASR_KEY）
load_dotenv()

# 音频参数（必须）
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 2048  # 640 * 2 = 1280 bytes

def open_microphone():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )
    return p, stream

if __name__ == "__main__":
    # 初始化 RTASR 客户端
    client = RtasrClient(
        app_id=os.getenv("RTASR_ID"),
        api_key=os.getenv("RTASR_KEY"),
        punc="1",          # 自动标点（可选）
        vad_mdn=2          # 端点检测（可选）
    )

    p, mic_stream = open_microphone()

    print("🎙️ 开始说话（Ctrl+C 结束）")

    try:
        for text in client.stream(mic_stream):
            print("识别结果：", text)
    except KeyboardInterrupt:
        print("\n🛑 停止录音")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()
