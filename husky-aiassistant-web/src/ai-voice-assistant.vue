<template>
  <div class="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- 头部 -->
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-indigo-600">AI 语音助手</h1>
      <!-- 添加右上角按钮 -->
      <button
          @click="router.push('/voice')"
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors flex items-center space-x-2"
      >
        <Settings class="w-5 h-5" />
        <span>语音模式</span>
      </button>
    </header>

    <!-- 对话区域 -->
    <div class="flex-1 overflow-y-auto px-4 py-6 space-y-4" ref="chatContainer">
      <div
          v-for="(message, index) in messages"
          :key="index"
          :class="[
          'flex',
          message.role === 'user' ? 'justify-end' : 'justify-start'
        ]"
      >
        <div
            :class="[
            'max-w-[70%] rounded-2xl px-4 py-3 shadow-md',
            message.role === 'user'
              ? 'bg-indigo-600 text-white'
              : 'bg-white text-gray-800'
          ]"
        >
          <p class="text-sm leading-relaxed">{{ message.content }}</p>
          <span class="text-xs opacity-70 mt-1 block">
            {{ formatTime(message.timestamp) }}
          </span>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-white rounded-2xl px-4 py-3 shadow-md">
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="bg-white border-t border-gray-200 px-4 py-4">
      <div class="flex items-center space-x-3 max-w-4xl mx-auto">
        <!-- 文本输入框 -->
        <input
            v-model="inputText"
            @keypress.enter="sendMessage"
            :disabled="isLoading || isListening"
            type="text"
            placeholder="输入消息或点击麦克风..."
            class="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />

        <!-- 麦克风按钮 -->
        <button
            @click="toggleVoiceRecognition"
            :disabled="isLoading"
            :class="[
            'p-3 rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed',
            isListening
              ? 'bg-red-500 hover:bg-red-600 animate-pulse'
              : 'bg-indigo-600 hover:bg-indigo-700'
          ]"
        >
          <Mic :class="['w-6 h-6 text-white']" />
        </button>

        <!-- 发送按钮 -->
        <button
            @click="sendMessage"
            :disabled="!inputText.trim() || isLoading || isListening"
            class="p-3 rounded-full bg-indigo-600 hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send class="w-6 h-6 text-white" />
        </button>
      </div>

      <!-- 语音识别状态提示 -->
      <div v-if="isListening" class="text-center mt-3">
        <p class="text-sm text-red-600 font-medium">正在聆听... 请说话</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="text-center mt-3">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>
    </div>
  </div>

</template>

<script setup>
import {ref, onMounted, nextTick} from 'vue'
import {Mic, Send, Settings} from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()


const messages = ref([])
const inputText = ref('')
const isLoading = ref(false)
const isListening = ref(false)
const error = ref('')
const chatContainer = ref(null)

let recognition = null
let audioPlayer = null

// 初始化语音识别
onMounted(() => {
  audioPlayer = new Audio()

  // 检查浏览器是否支持 Web Speech API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

  if (SpeechRecognition) {
    recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN' // 设置中文识别
    recognition.continuous = false // 单次识别
    recognition.interimResults = false // 不返回中间结果

    // 识别结果
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      inputText.value = transcript
      isListening.value = false

      // 自动发送语音识别的文本到 /voicechat 接口
      sendVoiceMessage(transcript)
    }

    // 识别错误
    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      error.value = `语音识别错误: ${event.error}`
      isListening.value = false
      setTimeout(() => {
        error.value = ''
      }, 3000)
    }

    // 识别结束
    recognition.onend = () => {
      isListening.value = false
    }
  } else {
    error.value = '您的浏览器不支持语音识别功能'
  }

  // 添加欢迎消息
  messages.value.push({
    role: 'assistant',
    content: '你好！我是AI语音助手，你可以通过输入文字或语音与我对话。',
    timestamp: new Date()
  })
})

// 切换语音识别
const toggleVoiceRecognition = () => {
  if (!recognition) {
    error.value = '语音识别不可用'
    return
  }

  if (isListening.value) {
    recognition.stop()
    isListening.value = false
  } else {
    error.value = ''
    inputText.value = ''
    isListening.value = true
    recognition.start()
  }
}

const sendVoiceMessage = async (message) => {
  if (!message || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })

  inputText.value = ''
  isLoading.value = true
  error.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用语音专用接口 /voicechat
    const response = await fetch('http://localhost:8000/voicechat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: message
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: data.reply || '抱歉，我没有收到有效的回复',
      timestamp: new Date()
    })

    await nextTick()
    scrollToBottom()

    if (data.audio_url) {
      audioPlayer.src = data.audio_url
      await audioPlayer.play()

      audioPlayer.onended = () => {
      }

      audioPlayer.onerror = (err) => {
        console.error('音频播放失败:', err)
        error.value = '音频播放失败'
        setTimeout(() => {
          error.value = ''
        }, 3000)
      }
    }

  } catch (err) {
    console.error('发送语音消息错误:', err)
    error.value = '语音消息发送失败，请检查网络连接或后端服务'

    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputText.value.trim()

  if (!message || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })

  inputText.value = ''
  isLoading.value = true
  error.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用后端接口
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: message
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: data.reply || '抱歉，我没有收到有效的回复',
      timestamp: new Date()
    })

  } catch (err) {
    console.error('发送消息错误:', err)
    error.value = '发送失败，请检查网络连接或后端服务'

    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>
