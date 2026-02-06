from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import asyncio
from enum import Enum
import pyaudio
import numpy as np
import pvporcupine
from faster_whisper import WhisperModel
import time
import tempfile
import wave
from dotenv import load_dotenv
import os
from .llm import call_llm
from .tts import text_to_mp3, play_mp3



load_dotenv()




router = APIRouter()


class AssistantState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


@router.websocket("/voice")
async def voice_ws(ws: WebSocket):
    await ws.accept()
    assistant = VoiceAssistant(ws)

    try:
        await assistant.start()
    except WebSocketDisconnect:
        print("client disconnected")
    except Exception as e:
        print("voice error:", e)
    finally:
        await assistant.shutdown()


class VoiceAssistant:
    def __init__(self, ws):
        self.ws = ws
        self.state = AssistantState.IDLE
        self.running = True
        self.waking = False
        self.tts_task = None

        self.MAX_RECORD_SECONDS = 10
        self.SILENCE_THRESHOLD = 300   # 音量阈值
        self.SILENCE_DURATION = 1.2    # 连续静音多久算结束



        # 先创建 porcupine
        self.porcupine = pvporcupine.create(
            access_key=os.getenv("PICOVOICE_ACCESS_KEY"),
            keywords=["porcupine"]  # 先用内置词
        )

        # 再用它的 frame_length
        self.RATE = 16000
        self.CHUNK = self.porcupine.frame_length

        self.audio = None
        self.stream = None

        self.whisper = WhisperModel(
            "small",
            device="cpu"
        )

    async def init_audio(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        print("🎤 mic initialized")

    async def release_audio(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("🎤 mic released")

    async def start(self):
        await self.init_audio()
        await self.set_state(AssistantState.IDLE)

        self.mic_task = asyncio.create_task(self.mic_listen_loop())

        while self.running:
            await asyncio.sleep(0.1)

    async def mic_listen_loop(self):
        while self.running:
            if self.state != AssistantState.IDLE or self.waking:
                await asyncio.sleep(0.05)
                continue

            data = await asyncio.to_thread(
                self.stream.read,
                self.CHUNK,
                exception_on_overflow=False
            )

            audio = np.frombuffer(data, dtype=np.int16)

            result = self.porcupine.process(audio)

            if result >= 0:
                print("🟢 Wake word detected")
                self.waking = True
                asyncio.create_task(self.on_wakeup())
                await asyncio.sleep(1)  # 防连击


    def calc_volume(self, audio_bytes):
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        return int(np.abs(audio_np).mean())

    async def on_wakeup(self):
        await self.set_state(AssistantState.LISTENING)
        await self.handle_asr()
        self.waking = False


    async def handle_asr(self):
        print("🎧 start recording...")
        frames = []

        silence_start = None
        start_time = time.time()

        while True:
            data = await asyncio.to_thread(
                self.stream.read,
                self.CHUNK,
                exception_on_overflow=False
            )

            frames.append(data)

            volume = self.calc_volume(data)

            if volume < self.SILENCE_THRESHOLD:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > self.SILENCE_DURATION:
                    print("🛑 silence detected, stop recording")
                    break
            else:
                silence_start = None

            if time.time() - start_time > self.MAX_RECORD_SECONDS:
                print("⏱ max record time reached")
                break

        # 保存 wav
        wav_path = self.save_wav(frames)

        await self.set_state(AssistantState.THINKING)

        text = await self.run_whisper(wav_path)

        print("📝 ASR result:", text)

        if text.strip():
            await self.handle_llm(text)
        else:
            await self.set_state(AssistantState.IDLE)

    def save_wav(self, frames):
        path = tempfile.mktemp(suffix=".wav")

        wf = wave.open(path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        return path

    async def run_whisper(self, wav_path: str) -> str:
        segments, info = await asyncio.to_thread(
            self.whisper.transcribe,
            wav_path,
            beam_size=5,
            language="zh"  # 中文
        )

        text = ""
        for seg in segments:
            text += seg.text

        return text.strip()

    async def handle_llm(self, text: str):
        await self.set_state(AssistantState.THINKING)

        try:
            print("🤖 calling LLM with:", text)
            reply = await self.run_llm(text)

            print("🤖 LLM reply:", reply)

            await self.set_state(AssistantState.SPEAKING)
            await self.handle_tts(reply)

        except Exception as e:
            print("❌ LLM error:", e)
            await self.set_state(AssistantState.IDLE)


    async def handle_tts(self, text: str):
        try:
            mp3_path = await text_to_mp3(text)
            await asyncio.to_thread(play_mp3, mp3_path)
        except Exception as e:
            print("❌ TTS error:", e)
        finally:
            await self.set_state(AssistantState.IDLE)


    async def shutdown(self):
        self.running = False

        if self.mic_task:
            self.mic_task.cancel()
            try:
                await self.mic_task
            except asyncio.CancelledError:
                pass

        if self.porcupine:
            self.porcupine.delete()

        await self.release_audio()

    async def set_state(self, state: AssistantState):
        self.state = state
        if not self.ws:
            print("STATE:", state.value)
            return
        try:
            await self.ws.send_json({"state": state.value})
        except Exception:
            self.running = False

    async def run_llm(self, text: str) -> str:
        # ⚠️ 一定要放线程池
        reply = await asyncio.to_thread(call_llm, text)
        return reply



# async def test_asr_only():
#     assistant = VoiceAssistant(ws=None)
#     await assistant.init_audio()
#
#     try:
#         await assistant.handle_asr()
#     finally:
#         await assistant.release_audio()
#
#
# if __name__ == "__main__":
#     asyncio.run(test_asr_only())

