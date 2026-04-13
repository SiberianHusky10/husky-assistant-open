import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AIVoiceAssistant from '../views/ai-voice-aiassistant.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/ai-voice-assistant'
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/ai-voice-assistant',
      name: 'AIVoiceAssistant',
      component: AIVoiceAssistant
    }
  ]
})

export default router