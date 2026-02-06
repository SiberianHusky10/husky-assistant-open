<template>
  <div class="voice-assistant">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="logo">
        <div class="logo-icon">🐺</div>
        <span class="logo-text">HuskyAI 语音助手</span>
      </div>
    </header>

    <!-- 中间动态圆形 -->
    <main class="main-content">
      <div class="voice-visualizer">
        <!-- 外层波纹圆环 -->
        <!-- 根据状态动态调整波纹速度和颜色 -->
        <div :class="['pulse-ring', 'pulse-ring-1', pulseClass]"></div>
        <div :class="['pulse-ring', 'pulse-ring-2', pulseClass]"></div>
        <div :class="['pulse-ring', 'pulse-ring-3', pulseClass]"></div>

        <!-- 中心圆 -->
        <!-- 根据不同状态改变中心圆的颜色 -->
        <div :class="['center-circle', circleClass]">
          <div class="inner-glow"></div>
          <svg class="mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
      </div>

      <!-- 状态文字 -->
      <div class="status-text">
        {{ statusText }}
      </div>

      <!-- 添加连接状态提示 -->
      <div v-if="!connected" class="connection-status">
        {{ connecting ? '正在连接到服务器...' : '连接已断开' }}
      </div>
    </main>

    <!-- 底部退出按钮 -->
    <footer class="footer">
      <button class="exit-button" @click="handleExit">
        <svg class="exit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
        <span>退出语音模式</span>
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const statusText = ref('正在连接...')
const currentState = ref('idle')
const ws = ref(null)
const connected = ref(false)
const connecting = ref(true)

const circleClass = computed(() => {
  switch (currentState.value) {
    case 'listening':
      return 'state-listening'
    case 'thinking':
      return 'state-thinking'
    case 'speaking':
      return 'state-speaking'
    default:
      return 'state-idle'
  }
})

const pulseClass = computed(() => {
  switch (currentState.value) {
    case 'listening':
      return 'pulse-fast'
    case 'thinking':
      return 'pulse-medium'
    case 'speaking':
      return 'pulse-slow'
    default:
      return ''
  }
})

const updateStatusText = (state) => {
  switch (state) {
    case 'idle':
      statusText.value = '待机中，请说唤醒词...'
      break
    case 'listening':
      statusText.value = '正在聆听...'
      break
    case 'thinking':
      statusText.value = '正在思考...'
      break
    case 'speaking':
      statusText.value = '正在回答...'
      break
    default:
      statusText.value = '未知状态'
  }
}

const connectWebSocket = () => {
  console.log('[v0] Connecting to WebSocket...')
  connecting.value = true

  // 连接到后端 /voice WebSocket 端点
  ws.value = new WebSocket('ws://localhost:8000/voice')

  ws.value.onopen = () => {
    console.log('[v0] WebSocket connected')
    connected.value = true
    connecting.value = false
    currentState.value = 'idle'
    updateStatusText('idle')
  }

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[v0] Received state:', data.state)

      // 更新状态
      currentState.value = data.state
      updateStatusText(data.state)
    } catch (error) {
      console.error('[v0] Failed to parse message:', error)
    }
  }

  ws.value.onerror = (error) => {
    console.error('[v0] WebSocket error:', error)
    connected.value = false
    connecting.value = false
  }

  ws.value.onclose = () => {
    console.log('[v0] WebSocket disconnected')
    connected.value = false
    connecting.value = false
    statusText.value = '连接已断开'

    // 5秒后自动重连
    setTimeout(() => {
      if (!connected.value) {
        console.log('[v0] Attempting to reconnect...')
        connectWebSocket()
      }
    }, 5000)
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) {
    console.log('[v0] Closing WebSocket connection')
    ws.value.close()
  }
})

const handleExit = () => {
  // 关闭 WebSocket 连接
  if (ws.value) {
    ws.value.close()
  }
  router.push('/')
}
</script>

<style scoped>
.voice-assistant {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 100%);
  display: flex;
  flex-direction: column;
  color: white;
  font-family: system-ui, -apple-system, sans-serif;
}

/* 顶部导航 */
.header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 2rem;
  animation: float 3s ease-in-out infinite;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 中间内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 3rem;
}

/* 语音可视化器 */
.voice-visualizer {
  position: relative;
  width: 280px;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 脉冲波纹效果 */
.pulse-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(59, 130, 246, 0.4);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 添加不同速度的脉冲动画 */
.pulse-ring.pulse-fast {
  animation-duration: 1s;
}

.pulse-ring.pulse-medium {
  animation-duration: 1.5s;
}

.pulse-ring.pulse-slow {
  animation-duration: 2.5s;
}

.pulse-ring-1 {
  width: 100%;
  height: 100%;
  animation-delay: 0s;
}

.pulse-ring-2 {
  width: 80%;
  height: 80%;
  animation-delay: 0.3s;
}

.pulse-ring-3 {
  width: 60%;
  height: 60%;
  animation-delay: 0.6s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.9);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.3;
  }
}

/* 中心圆 */
.center-circle {
  position: relative;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.5s ease;
}

/* 添加不同状态的中心圆颜色 */
.center-circle.state-idle {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  box-shadow: 0 0 60px rgba(59, 130, 246, 0.6), 0 0 100px rgba(139, 92, 246, 0.4);
}

.center-circle.state-listening {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 0 60px rgba(239, 68, 68, 0.8), 0 0 100px rgba(220, 38, 38, 0.5);
}

.center-circle.state-thinking {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 0 60px rgba(245, 158, 11, 0.8), 0 0 100px rgba(217, 119, 6, 0.5);
}

.center-circle.state-speaking {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 0 60px rgba(16, 185, 129, 0.8), 0 0 100px rgba(5, 150, 105, 0.5);
}

.center-circle:hover {
  transform: scale(1.05);
}

.inner-glow {
  position: absolute;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  animation: innerPulse 2s ease-in-out infinite;
}

@keyframes innerPulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(0.9);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1);
  }
}

/* 麦克风图标 */
.mic-icon {
  width: 48px;
  height: 48px;
  color: white;
  z-index: 1;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
}

/* 状态文字 */
.status-text {
  font-size: 1.5rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  animation: fadeInOut 2s ease-in-out infinite;
}

/* 添加连接状态提示样式 */
.connection-status {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 8px;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 底部 */
.footer {
  padding: 2rem;
  display: flex;
  justify-content: center;
}

/* 退出按钮 */
.exit-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.exit-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.exit-button:active {
  transform: translateY(0);
}

.exit-icon {
  width: 20px;
  height: 20px;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .header {
    padding: 1rem 1.5rem;
  }

  .logo-text {
    font-size: 1.1rem;
  }

  .voice-visualizer {
    width: 240px;
    height: 240px;
  }

  .center-circle {
    width: 140px;
    height: 140px;
  }

  .mic-icon {
    width: 40px;
    height: 40px;
  }

  .status-text {
    font-size: 1.25rem;
  }

  .exit-button {
    padding: 0.875rem 1.5rem;
    font-size: 0.95rem;
  }
}
</style>
