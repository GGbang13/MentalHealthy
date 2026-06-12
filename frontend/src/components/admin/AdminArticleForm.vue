<template>
  <el-card shadow="never" class="form-card">
    <template #header>
      <div class="form-head">
        <div>
          <div class="eyebrow">{{ mode === 'create' ? '新建文章' : '编辑文章' }}</div>
          <h2>{{ mode === 'create' ? '发布新的心理文章' : '更新文章内容与状态' }}</h2>
          <p>字段与后端接口保持一致，保存后立即写入后台文章数据。</p>
        </div>
      </div>
    </template>

    <el-form ref="formRef" :model="model" :rules="rules" label-width="88px" class="article-form">
      <el-form-item label="标题" prop="title">
        <el-input v-model="model.title" maxlength="80" show-word-limit placeholder="请输入文章标题" />
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-input v-model="model.category" maxlength="30" show-word-limit placeholder="如：心理科普、情绪管理" />
      </el-form-item>
      <el-form-item label="摘要" prop="summary">
        <el-input
          v-model="model.summary"
          type="textarea"
          :rows="4"
          maxlength="240"
          show-word-limit
          placeholder="请输入文章摘要"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="model.status" placeholder="请选择文章状态">
          <el-option label="已发布" value="PUBLISHED" />
          <el-option label="草稿" value="DRAFT" />
        </el-select>
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input
          v-model="model.content"
          type="textarea"
          :rows="16"
          maxlength="12000"
          show-word-limit
          placeholder="请输入文章正文内容"
        />
      </el-form-item>
    </el-form>

    <div class="form-actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">保存文章</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

export interface ArticleFormModel {
  title: string
  category: string
  summary: string
  content: string
  status: 'PUBLISHED' | 'DRAFT'
}

const props = defineProps<{
  model: ArticleFormModel
  mode: 'create' | 'edit'
  submitting?: boolean
}>()

const emit = defineEmits<{
  submit: []
  cancel: []
}>()

const formRef = ref<FormInstance>()

const rules: FormRules<ArticleFormModel> = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 2, max: 80, message: '标题长度需在 2 到 80 个字符之间', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请输入文章分类', trigger: 'blur' },
    { min: 2, max: 30, message: '分类长度需在 2 到 30 个字符之间', trigger: 'blur' }
  ],
  summary: [
    { required: true, message: '请输入文章摘要', trigger: 'blur' },
    { min: 10, max: 240, message: '摘要长度需在 10 到 240 个字符之间', trigger: 'blur' }
  ],
  status: [{ required: true, message: '请选择文章状态', trigger: 'change' }],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 20, max: 12000, message: '内容长度需在 20 到 12000 个字符之间', trigger: 'blur' }
  ]
}

const submit = async () => {
  await formRef.value?.validate()
  emit('submit')
}

defineExpose({
  validate: () => formRef.value?.validate()
})
</script>

<style scoped lang="scss">
.form-card { border-radius: 22px; }
.form-head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.eyebrow { color: #c2410c; font-size: 13px; font-weight: 700; }
.form-head h2 { margin: 8px 0 10px; color: #0f172a; }
.form-head p { margin: 0; color: #64748b; line-height: 1.7; }
.article-form { max-width: 980px; }
.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px; }
</style>
