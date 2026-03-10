import { createRouter, createWebHistory } from 'vue-router'
import Chat from '@/ai-voice-assistant.vue'
import VoiceAssistant from "@/voice-assistant.vue";

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
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router