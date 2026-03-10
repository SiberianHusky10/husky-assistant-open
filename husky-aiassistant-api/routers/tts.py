import edge_tts
import os
import time
import asyncio
import tempfile
import pygame
import threading

VOICE_ZH = "zh-CN-XiaoxiaoNeural"

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def text_to_mp3(text: str) -> str:
    # 在当前目录创建临时 mp3 文件
    fd, path = tempfile.mkstemp(
        suffix=".mp3",
        dir=BASE_DIR
    )
    os.close(fd)  # 关闭文件描述符，edge-tts 会写入

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE_ZH,
        rate="+0%",
        volume="+0%"
    )

    await communicate.save(path)
    return path


def delayed_delete(path: str, delay: float):
    """延迟删除文件"""
    time.sleep(delay)
    try:
        os.remove(path)
        print(f"🧹 已删除: {path}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")


def play_mp3(path: str, delete_after: float = 3.0):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

    # ✅ 等待播放真正开始
    start_time = time.time()
    while not pygame.mixer.music.get_busy():
        if time.time() - start_time > 1.0:
            break
        time.sleep(0.01)

    # ✅ 等待播放结束
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

    # ✅ 延迟删除（非 daemon，捕获异常）
    threading.Thread(
        target=delayed_delete,
        args=(path, delete_after),
    ).start()
