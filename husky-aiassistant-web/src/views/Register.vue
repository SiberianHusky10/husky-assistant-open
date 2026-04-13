<template>
  <div class="card">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800">注册</h1>
    
    <form @submit.prevent="handleRegister" class="space-y-6">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
        <input
          type="email"
          id="email"
          v-model="form.email"
          class="input-field"
          placeholder="请输入邮箱"
          @blur="validateEmail"
        />
        <p v-if="errors.email" class="error-message">{{ errors.email }}</p>
      </div>
      
      <div class="flex space-x-3">
        <div class="flex-1">
          <label for="code" class="block text-sm font-medium text-gray-700 mb-1">验证码</label>
          <input
            type="text"
            id="code"
            v-model="form.code"
            class="input-field"
            placeholder="请输入验证码"
            @blur="validateCode"
          />
          <p v-if="errors.code" class="error-message">{{ errors.code }}</p>
        </div>
        <div class="w-32 flex items-end">
          <button
            type="button"
            class="btn-secondary w-full"
            :disabled="countdown > 0 || !form.email"
            @click="sendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </div>
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
        <input
          type="password"
          id="password"
          v-model="form.password"
          class="input-field"
          placeholder="请设置密码"
          @blur="validatePassword"
        />
        <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
      </div>
      
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
        <input
          type="password"
          id="confirmPassword"
          v-model="form.confirmPassword"
          class="input-field"
          placeholder="请确认密码"
          @blur="validateConfirmPassword"
        />
        <p v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</p>
      </div>
      
      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? '注册中...' : '注册' }}
      </button>
      
      <div class="text-center">
        <span class="text-gray-600">已有账号？</span>
        <router-link to="/login" class="link ml-1">立即登录</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const countdown = ref(0)
let countdownTimer: number | null = null

const validateEmail = () => {
  if (!form.email) {
    errors.email = '请输入邮箱'
    return false
  }
  
  // 邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    errors.email = '请输入有效的邮箱'
    return false
  }
  
  errors.email = ''
  return true
}

const validateCode = () => {
  if (!form.code) {
    errors.code = '请输入验证码'
    return false
  }
  
  if (form.code.length !== 6) {
    errors.code = '验证码应为6位数字'
    return false
  }
  
  errors.code = ''
  return true
}

const validatePassword = () => {
  if (!form.password) {
    errors.password = '请设置密码'
    return false
  }
  
  if (form.password.length < 6 || form.password.length > 20) {
    errors.password = '密码长度应在6-20位之间'
    return false
  }
  
  errors.password = ''
  return true
}

const validateConfirmPassword = () => {
  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    return false
  }
  
  if (form.confirmPassword !== form.password) {
    errors.confirmPassword = '两次输入的密码不一致'
    return false
  }
  
  errors.confirmPassword = ''
  return true
}

const sendCode = () => {
  if (!validateEmail()) {
    return
  }
  
  // 模拟发送验证码 API 调用
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
    // 开始倒计时
    startCountdown()
  }, 1000)
}

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownTimer!)
    }
  }, 1000)
}

const handleRegister = async () => {
  const isEmailValid = validateEmail()
  const isCodeValid = validateCode()
  const isPasswordValid = validatePassword()
  const isConfirmPasswordValid = validateConfirmPassword()
  
  if (!isEmailValid || !isCodeValid || !isPasswordValid || !isConfirmPasswordValid) {
    return
  }
  
  isLoading.value = true
  
  // 模拟注册 API 调用
  setTimeout(() => {
    isLoading.value = false
    // 注册成功，跳转到登录页面
    router.push('/login')
  }, 1000)
}

// 组件卸载时清除倒计时
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
/* Register-specific styles */
</style>