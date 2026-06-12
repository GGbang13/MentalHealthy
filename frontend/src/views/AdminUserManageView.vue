<template>
  <div class="manage-page">
    <div class="header-row">
      <div>
        <div class="eyebrow">用户管理</div>
        <h2>分开查看普通用户与管理员列表</h2>
      </div>
    </div>

    <el-card shadow="never">
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索用户名、昵称、邮箱" />
        <el-select v-model="roleFilter" placeholder="账号类型">
          <el-option label="普通用户" value="USER" />
          <el-option label="管理员" value="ADMIN" />
        </el-select>
        <el-button type="primary" @click="loadData">筛查</el-button>
      </div>

      <el-table :data="users">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" min-width="160" />
        <el-table-column prop="status" label="状态" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import http from '@/api/http'
import type { AdminUser } from '@/types'

interface UserPageResult {
  records: AdminUser[]
  total: number
}

const users = ref<AdminUser[]>([])
const keyword = ref('')
const roleFilter = ref<'USER' | 'ADMIN'>('USER')

const loadData = async () => {
  const res = await http.get<UserPageResult>('/admin/users', {
    params: { role: roleFilter.value, keyword: keyword.value, current: 1, size: 100 }
  })
  users.value = res.records
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.manage-page { display: grid; gap: 18px; }
.header-row, .toolbar { display: flex; flex-wrap: wrap; gap: 12px; }
.header-row { justify-content: space-between; align-items: center; }
.eyebrow { color: #2563eb; font-size: 13px; font-weight: 700; }
.header-row h2 { margin: 8px 0 0; }
</style>
