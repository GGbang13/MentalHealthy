<template>
  <div class="page-wrap">
    <AdminArticleForm
      :model="form"
      mode="create"
      :submitting="submitting"
      @submit="submit"
      @cancel="router.push('/admin/articles')"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import AdminArticleForm, { type ArticleFormModel } from '@/components/admin/AdminArticleForm.vue'

const router = useRouter()
const submitting = ref(false)
const form = reactive<ArticleFormModel>({
  title: '',
  category: '心理科普',
  summary: '',
  content: '',
  status: 'PUBLISHED'
})

const submit = async () => {
  try {
    submitting.value = true
    await http.post('/articles', form)
    ElMessage.success('文章已创建')
    router.push('/admin/articles')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.page-wrap { display: grid; gap: 18px; }
</style>
