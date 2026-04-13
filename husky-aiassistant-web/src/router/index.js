import { createRouter, createWebHistory } from 'vue-router'
import Chat from '@/views/ai-voice-assistant.vue'
import VoiceAssistant from "@/voice-assistant.vue";
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

const routes = [
    {
        path: '/',
        name: 'Chat',
        component: Chat
    },
    {
        path: '/voice',
        name: 'VoiceAssistant',
        component: VoiceAssistant
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
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router