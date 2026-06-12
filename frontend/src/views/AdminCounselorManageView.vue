<template>
  <div class="manage-page">
    <div class="header-row">
      <div>
        <div class="eyebrow">咨询师管理</div>
        <h2>按列表查看咨询师账号与档案</h2>
      </div>
    </div>

    <el-card shadow="never">
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索用户名、昵称、擅长方向" />
        <el-button type="primary" @click="loadData">筛查</el-button>
      </div>

      <el-table :data="counselors">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="title" label="职称" min-width="160" />
        <el-table-column prop="specialties" label="擅长方向" min-width="200" />
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

const counselors = ref<AdminUser[]>([])
const keyword = ref('')

const loadData = async () => {
  const res = await http.get<UserPageResult>('/admin/users', {
    params: { role: 'COUNSELOR', keyword: keyword.value, current: 1, size: 100 }
  })
  counselors.value = res.records
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.manage-page { display: grid; gap: 18px; }
.header-row, .toolbar { display: flex; flex-wrap: wrap; gap: 12px; }
.header-row { justify-content: space-between; align-items: center; }
.eyebrow { color: #0f766e; font-size: 13px; font-weight: 700; }
.header-row h2 { margin: 8px 0 0; }
</style>
