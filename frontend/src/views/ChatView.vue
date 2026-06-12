<template>
  <div class="chat-page">
    <el-card shadow="never" class="sidebar">
      <template #header>
        <div class="sidebar-header">
          <div>
            <h3>聊天对象</h3>
            <p>仅显示已确认预约或已有历史会话的联系人。</p>
          </div>
        </div>
      </template>

      <div class="contact-list">
        <button
          v-for="contact in contacts"
          :key="contact.userId"
          type="button"
          class="contact-row"
          :class="{ active: peerId === String(contact.userId) }"
          @click="selectPeer(contact.userId)"
        >
          <div class="contact-avatar">{{ (contact.nickname || contact.username || 'U').slice(0, 1) }}</div>
          <div class="contact-text">
            <div class="contact-title-row">
              <strong>{{ contact.nickname || contact.username || `用户#${contact.userId}` }}</strong>
              <el-tag size="small" effect="plain" :type="contact.role === 'COUNSELOR' ? 'success' : 'info'">
                {{ contact.role === 'COUNSELOR' ? '咨询师' : contact.role === 'USER' ? '来访者' : contact.role || '联系人' }}
              </el-tag>
            </div>
            <span>{{ contact.title || '已建立沟通关系' }}</span>
            <small>{{ contact.specialties || '点击查看会话记录' }}</small>
          </div>
        </button>
        <el-empty v-if="!contacts.length" description="暂无可聊天对象" />
      </div>
    </el-card>

    <el-card shadow="never" class="chat-panel">
      <template #header>
        <div class="thread-header">
          <div>
            <h3>{{ activeContactName }}</h3>
            <p>{{ activeContactSubline }}</p>
          </div>
          <el-tag v-if="peerId" type="success" effect="plain">实时会话</el-tag>
        </div>
      </template>

      <div ref="messageContainer" class="messages">
        <div v-if="messages.length" class="message-list">
          <div
            v-for="item in messages"
            :key="item.id"
            class="message-row"
            :class="{ self: item.senderId === userStore.user?.id }"
          >
            <div class="message-bubble">
              <p>{{ item.content }}</p>
              <div class="message-meta">
                <span>{{ item.reviewStatus === 'APPROVED' ? '已发送' : item.reviewStatus }}</span>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else :description="peerId ? '当前还没有聊天记录' : '请先选择左侧联系人'" />
      </div>

      <div class="composer">
        <el-input
          v-model="content"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="输入消息内容。系统会进行敏感词过滤。"
          @keydown.ctrl.enter.prevent="sendMessage"
        />
        <div class="composer-actions">
          <el-input v-model="fileUrl" placeholder="文件地址（可选）" />
          <el-button type="primary" :disabled="!peerId" @click="sendMessage">发送</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import http from '@/api/http'
import { useUserStore } from '@/stores/user'
import type { ChatContact, ChatMessage } from '@/types'

const route = useRoute()
const userStore = useUserStore()
const peerId = ref('')
const content = ref('')
const fileUrl = ref('')
const messages = ref<ChatMessage[]>([])
const contacts = ref<ChatContact[]>([])
const messageContainer = ref<HTMLDivElement | null>(null)
let socket: WebSocket | null = null

const activeContact = computed(
  () => contacts.value.find((contact) => String(contact.userId) === peerId.value) ?? null
)

const activeContactName = computed(() => {
  if (!activeContact.value) return '在线聊天'
  return activeContact.value.nickname || activeContact.value.username || `用户#${activeContact.value.userId}`
})

const activeContactSubline = computed(() => {
  if (!activeContact.value) return '选择左侧联系人后即可查看历史消息并继续沟通。'
  return activeContact.value.specialties || activeContact.value.title || activeContact.value.role || '聊天对象'
})

const scrollToBottom = async () => {
  await nextTick()
  const el = messageContainer.value
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

const upsertMessage = async (message: ChatMessage) => {
  const exists = messages.value.some((item) => item.id === message.id)
  if (exists) {
    messages.value = messages.value.map((item) => item.id === message.id ? message : item)
  } else {
    const nextMessages = [...messages.value, message]
    nextMessages.sort((left, right) => left.id - right.id)
    messages.value = nextMessages
  }
  await scrollToBottom()
}

const ensureContact = async (id: string) => {
  if (!id || contacts.value.some((item) => String(item.userId) === id)) {
    return
  }
  await loadContacts()
}

const loadContacts = async () => {
  contacts.value = await http.get<ChatContact[]>('/chat/contacts')
}

const loadHistory = async () => {
  if (!peerId.value) return
  messages.value = await http.get<ChatMessage[]>(`/chat/history/${peerId.value}`)
  await scrollToBottom()
}

const sendMessage = async () => {
  if (!peerId.value || !content.value.trim()) {
    ElMessage.warning('请选择聊天对象并输入消息内容')
    return
  }
  const saved = await http.post<ChatMessage>('/chat/send', {
    receiverId: Number(peerId.value),
    content: content.value.trim(),
    fileUrl: fileUrl.value
  })
  await upsertMessage(saved)
  content.value = ''
  fileUrl.value = ''
}

const selectPeer = async (id: number) => {
  peerId.value = String(id)
  await loadHistory()
}

const connectWebSocket = () => {
  if (!userStore.token || socket) return
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat?token=${encodeURIComponent(userStore.token)}`)
  socket.onmessage = async (event) => {
    const incoming = JSON.parse(event.data) as ChatMessage
    const activePeerId = Number(peerId.value)
    const currentUserId = userStore.user?.id
    const belongsToCurrentThread =
      incoming.senderId === activePeerId ||
      incoming.receiverId === activePeerId ||
      (incoming.senderId === currentUserId && incoming.receiverId === activePeerId)

    if (belongsToCurrentThread) {
      await upsertMessage(incoming)
    } else {
      await loadContacts()
    }
  }
  socket.onerror = () => {
    ElMessage.warning('实时连接异常，当前页面会继续使用接口收发消息')
  }
  socket.onclose = () => {
    socket = null
  }
}

watch(
  () => route.query.peerId,
  async (value) => {
    if (!value) return
    peerId.value = String(value)
    await ensureContact(peerId.value)
    await loadHistory()
  },
  { immediate: true }
)

onMounted(async () => {
  connectWebSocket()
  await loadContacts()
  if (peerId.value) {
    await ensureContact(peerId.value)
    await loadHistory()
  }
})

onBeforeUnmount(() => {
  socket?.close()
  socket = null
})
</script>

<style scoped lang="scss">
.chat-page {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
  min-height: calc(100vh - 220px);
}

.sidebar,
.chat-panel {
  min-height: 100%;
}

.sidebar-header h3,
.sidebar-header p,
.thread-header h3,
.thread-header p {
  margin: 0;
}

.sidebar-header p,
.thread-header p {
  margin-top: 6px;
  color: #64748b;
  line-height: 1.6;
}

.contact-list {
  display: grid;
  gap: 10px;
}

.contact-row {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: 0.2s ease;
}

.contact-row:hover,
.contact-row.active {
  border-color: #93c5fd;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
}

.contact-avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #0f766e, #38bdf8);
}

.contact-text {
  display: grid;
  gap: 4px;
}

.contact-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.contact-text strong {
  color: #0f172a;
}

.contact-text span,
.contact-text small {
  color: #64748b;
}

.thread-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.messages {
  height: 460px;
  overflow: auto;
  padding: 6px 4px 6px 0;
}

.message-list {
  display: grid;
  gap: 14px;
}

.message-row {
  display: flex;
}

.message-row.self {
  justify-content: flex-end;
}

.message-bubble {
  max-width: min(72%, 560px);
  padding: 14px 16px;
  border-radius: 20px;
  background: #f5f0e8;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.message-row.self .message-bubble {
  background: linear-gradient(135deg, rgba(32, 92, 79, 0.12), rgba(56, 189, 248, 0.12));
}

.message-bubble p {
  margin: 0;
  line-height: 1.7;
  color: #0f172a;
  white-space: pre-wrap;
}

.message-meta {
  margin-top: 8px;
  color: #64748b;
  font-size: 12px;
}

.composer {
  margin-top: 16px;
  display: grid;
  gap: 12px;
}

.composer-actions {
  display: grid;
  grid-template-columns: 1fr 120px;
  gap: 12px;
}

@media (max-width: 960px) {
  .chat-page {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .messages {
    height: 360px;
  }
}
</style>
