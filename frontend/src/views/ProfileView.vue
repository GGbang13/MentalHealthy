<template>
  <div class="profile-page">
    <el-card shadow="never">
      <template #header>基础资料</template>
      <el-form :model="form" label-width="100px" class="profile-form">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" disabled />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" clearable placeholder="请选择性别">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.profile" type="textarea" :rows="4" placeholder="介绍一下你自己" />
        </el-form-item>
        <el-button type="primary" @click="save">保存基础资料</el-button>
      </el-form>
    </el-card>

    <el-card v-if="isCounselor" shadow="never">
      <template #header>咨询师专业档案</template>
      <el-form :model="counselorForm" label-width="110px" class="profile-form">
        <el-form-item label="职称">
          <el-input v-model="counselorForm.title" placeholder="例如：国家二级心理咨询师" />
        </el-form-item>
        <el-form-item label="擅长方向">
          <el-input v-model="counselorForm.specialties" placeholder="例如：情绪疏导、亲密关系、青少年成长" />
        </el-form-item>
        <el-form-item label="从业年限">
          <el-input-number v-model="counselorForm.yearsOfExperience" :min="0" :max="50" />
        </el-form-item>
        <el-form-item label="咨询价格">
          <el-input-number v-model="counselorForm.pricePerHour" :min="0" :max="5000" :step="50" />
        </el-form-item>
        <el-form-item label="在线状态">
          <el-switch v-model="counselorOnline" />
        </el-form-item>
        <el-form-item label="专业简介">
          <el-input
            v-model="counselorForm.introduction"
            type="textarea"
            :rows="5"
            placeholder="介绍你的咨询经验、服务对象和工作方式"
          />
        </el-form-item>
        <el-button type="primary" @click="saveCounselor">保存咨询师档案</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/api/http'
import { useUserStore, type UserInfo } from '@/stores/user'
import type { Counselor } from '@/types'

interface CounselorProfilePayload {
  title: string
  specialties: string
  yearsOfExperience: number
  introduction: string
  pricePerHour: number
  onlineStatus: number
  scheduleJson: string | null
}

const userStore = useUserStore()
const form = reactive<Partial<UserInfo>>({
  id: undefined,
  username: '',
  nickname: '',
  role: '',
  email: '',
  phone: '',
  avatar: '',
  gender: '',
  age: undefined,
  profile: ''
})

const counselorForm = reactive<CounselorProfilePayload>({
  title: '',
  specialties: '',
  yearsOfExperience: 0,
  introduction: '',
  pricePerHour: 0,
  onlineStatus: 0,
  scheduleJson: ''
})

const isCounselor = computed(() => userStore.user?.role === 'COUNSELOR')
const counselorOnline = computed({
  get: () => counselorForm.onlineStatus === 1,
  set: (value: boolean) => {
    counselorForm.onlineStatus = value ? 1 : 0
  }
})

const loadBaseProfile = async () => {
  const profile = await http.get<UserInfo>('/users/me')
  Object.assign(form, profile)
}

const loadCounselorProfile = async () => {
  if (!isCounselor.value) return
  const profile = await http.get<Counselor>('/counselors/me')
  counselorForm.title = profile.title || ''
  counselorForm.specialties = profile.specialties || ''
  counselorForm.yearsOfExperience = Number(profile.yearsOfExperience || 0)
  counselorForm.introduction = profile.introduction || ''
  counselorForm.pricePerHour = Number(profile.pricePerHour || 0)
  counselorForm.onlineStatus = Number(profile.onlineStatus || 0)
  counselorForm.scheduleJson = profile.scheduleJson || ''
}

const save = async () => {
  try {
    await http.put('/users/me', {
      nickname: form.nickname,
      avatar: form.avatar,
      gender: form.gender,
      age: form.age,
      profile: form.profile
    })
    await userStore.fetchProfile()
    await loadBaseProfile()
    ElMessage.success('资料已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存基础资料失败')
  }
}

const saveCounselor = async () => {
  try {
    await http.put('/counselors/me', {
      title: counselorForm.title.trim(),
      specialties: counselorForm.specialties.trim(),
      yearsOfExperience: Number(counselorForm.yearsOfExperience || 0),
      introduction: counselorForm.introduction.trim(),
      pricePerHour: Number(counselorForm.pricePerHour || 0),
      onlineStatus: counselorForm.onlineStatus,
      scheduleJson: counselorForm.scheduleJson?.trim() ? counselorForm.scheduleJson.trim() : null
    })
    await loadCounselorProfile()
    ElMessage.success('咨询师档案已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存咨询师档案失败')
  }
}

onMounted(async () => {
  await loadBaseProfile()
  await loadCounselorProfile()
})
</script>

<style scoped lang="scss">
.profile-page {
  display: grid;
  gap: 20px;
}

.profile-form {
  max-width: 620px;
}
</style>
