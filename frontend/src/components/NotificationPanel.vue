<template>
  <el-card shadow="never" class="notice-card">
    <template #header>
      <div class="notice-head">
        <div>
          <h3>通知中心</h3>
          <p>查看管理员发给你或当前角色的通知。</p>
        </div>
        <el-button text @click="loadNotifications">刷新</el-button>
      </div>
    </template>

    <div v-if="notifications.length" class="notice-list">
      <div v-for="item in notifications" :key="item.id" class="notice-item">
        <div class="notice-badge">通知</div>
        <div class="notice-body">
          <strong>{{ item.title || '平台通知' }}</strong>
          <p>{{ item.content || '暂无内容' }}</p>
          <span>{{ formatDate(item.createdAt) }}</span>
        </div>
      </div>
    </div>
    <el-empty v-else description="当前还没有通知" />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import http from '@/api/http'
import type { NotificationItem } from '@/types'

const notifications = ref<NotificationItem[]>([])

const loadNotifications = async () => {
  notifications.value = await http.get<NotificationItem[]>('/users/notifications')
}

const formatDate = (value?: string) => value ? value.replace('T', ' ').slice(0, 16) : '刚刚'

onMounted(loadNotifications)
</script>

<style scoped lang="scss">
.notice-card { display: grid; }
.notice-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.notice-head h3, .notice-head p { margin: 0; }
.notice-head p { margin-top: 6px; color: #64748b; line-height: 1.6; }
.notice-list { display: grid; gap: 12px; }
.notice-item { display: grid; grid-template-columns: 56px 1fr; gap: 14px; padding: 16px; border-radius: 18px; background: linear-gradient(135deg, #fff7ed, #f8fafc); border: 1px solid #fed7aa; }
.notice-badge { width: 56px; height: 56px; border-radius: 18px; display: grid; place-items: center; background: #fb923c; color: #fff; font-size: 13px; font-weight: 700; }
.notice-body { display: grid; gap: 6px; }
.notice-body strong { color: #0f172a; }
.notice-body p { margin: 0; color: #475569; line-height: 1.7; }
.notice-body span { color: #94a3b8; font-size: 12px; }
</style>
