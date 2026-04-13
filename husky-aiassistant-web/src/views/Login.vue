<template>
  <div class="card">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800">登录</h1>
    
    <form @submit.prevent="handleLogin" class="space-y-6">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">邮箱/手机号</label>
        <input
          type="text"
          id="email"
          v-model="form.email"
          class="input-field"
          placeholder="请输入邮箱或手机号"
          @blur="validateEmail"
        />
        <p v-if="errors.email" class="error-message">{{ errors.email }}</p>
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
        <input
          type="password"
          id="password"
          v-model="form.password"
          class="input-field"
          placeholder="请输入密码"
          @blur="validatePassword"
        />
        <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
      </div>
      
      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
      
      <div class="text-center">
        <span class="text-gray-600">还没有账号？</span>
        <router-link to="/register" class="link ml-1">立即注册</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const isLoading = ref(false)

const validateEmail = () => {
  if (!form.email) {
    errors.email = '请输入邮箱或手机号'
    return false
  }
  
  // 简单的邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const phoneRegex = /^1[3-9]\d{9}$/
  
  if (!emailRegex.test(form.email) && !phoneRegex.test(form.email)) {
    errors.email = '请输入有效的邮箱或手机号'
    return false
  }
  
  errors.email = ''
  return true
}

const validatePassword = () => {
  if (!form.password) {
    errors.password = '请输入密码'
    return false
  }
  
  if (form.password.length < 6 || form.password.length > 20) {
    errors.password = '密码长度应在6-20位之间'
    return false
  }
  
  errors.password = ''
  return true
}

const handleLogin = async () => {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  
  if (!isEmailValid || !isPasswordValid) {
    return
  }
  
  isLoading.value = true
  
  // 模拟登录 API 调用
  setTimeout(() => {
    isLoading.value = false
    // 登录成功，这里可以存储 token 到 localStorage
    localStorage.setItem('token', 'mock-token')
    // 重定向到首页（这里简单重定向到登录页，实际项目中应重定向到应用主页）
    router.push('/')
  }, 1000)
}
</script>

<style scoped>
/* Login-specific styles */
</style>