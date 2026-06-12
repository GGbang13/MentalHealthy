<template>
  <div class="manage-page">
    <div class="header-row">
      <div>
        <div class="eyebrow">通知管理</div>
        <h2>管理员向用户和咨询师发布通知</h2>
      </div>
    </div>

    <el-card shadow="never">
      <template #header>发布通知</template>
      <el-form :model="form" label-width="90px" class="publish-form">
        <el-form-item label="通知对象">
          <el-select v-model="form.targetRole" placeholder="请选择通知对象">
            <el-option label="普通用户" value="USER" />
            <el-option label="咨询师" value="COUNSELOR" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知标题">
          <el-input v-model="form.title" maxlength="60" show-word-limit placeholder="请输入通知标题" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            maxlength="500"
            show-word-limit
            placeholder="请输入通知内容"
          />
        </el-form-item>
        <div class="form-actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" @click="submitNotification">发布通知</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div class="list-head">
          <span>已发布通知</span>
          <div class="list-actions">
            <el-select v-model="filterRole" clearable placeholder="筛选对象">
              <el-option label="普通用户" value="USER" />
              <el-option label="咨询师" value="COUNSELOR" />
            </el-select>
            <el-button text @click="loadNotifications">刷新</el-button>
          </div>
        </div>
      </template>

      <div v-if="notifications.length" class="notice-list">
        <div v-for="item in notifications" :key="item.id" class="notice-item">
          <div class="notice-top">
            <strong>{{ item.title || '平台通知' }}</strong>
            <el-tag size="small" :type="item.targetRole === 'COUNSELOR' ? 'success' : 'primary'">
              {{ item.targetRole === 'COUNSELOR' ? '咨询师' : '普通用户' }}
            </el-tag>
          </div>
          <p>{{ item.content || '暂无内容' }}</p>
          <span>{{ formatDate(item.createdAt) }}</span>
        </div>
      </div>
      <el-empty v-else description="当前还没有已发布通知" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/api/http'
import type { NotificationItem } from '@/types'

const notifications = ref<NotificationItem[]>([])
const filterRole = ref<'USER' | 'COUNSELOR' | ''>('')

const form = reactive({
  targetRole: 'USER' as 'USER' | 'COUNSELOR',
  title: '',
  content: ''
})

const loadNotifications = async () => {
  notifications.value = await http.get<NotificationItem[]>('/admin/notifications', {
    params: {
      targetRole: filterRole.value || undefined
    }
  })
}

const resetForm = () => {
  form.targetRole = 'USER'
  form.title = ''
  form.content = ''
}

const submitNotification = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('请填写通知标题和内容')
    return
  }
  await http.post('/admin/notifications', {
    targetRole: form.targetRole,
    title: form.title.trim(),
    content: form.content.trim()
  })
  ElMessage.success('通知已发布')
  resetForm()
  await loadNotifications()
}

const formatDate = (value?: string) => value ? value.replace('T', ' ').slice(0, 16) : '刚刚'

watch(filterRole, loadNotifications)

onMounted(loadNotifications)
</script>

<style scoped lang="scss">
.manage-page { display: grid; gap: 18px; }
.header-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.eyebrow { color: #7c3aed; font-size: 13px; font-weight: 700; }
.header-row h2 { margin: 8px 0 0; }
.publish-form { max-width: 760px; }
.form-actions { display: flex; justify-content: flex-end; gap: 12px; }
.list-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.list-actions { display: flex; align-items: center; gap: 12px; }
.notice-list { display: grid; gap: 12px; }
.notice-item { display: grid; gap: 8px; padding: 16px; border-radius: 16px; background: #faf5ff; border: 1px solid #e9d5ff; }
.notice-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.notice-item p { margin: 0; color: #475569; line-height: 1.7; }
.notice-item span { color: #94a3b8; font-size: 12px; }
</style>
