<template>
  <div class="auth-page">
    <div class="auth-backdrop auth-backdrop-left" />
    <div class="auth-backdrop auth-backdrop-right" />

    <section class="auth-showcase">
      <div class="showcase-badge">
        <span class="showcase-dot" />
        心理健康支持平台
      </div>

      <div class="showcase-copy">
        <p class="showcase-kicker">温和陪伴，安心开始</p>
        <h1>在这里，慢一点也没关系。</h1>
        <p class="showcase-text">
          你可以从心理测评开始了解自己，也可以预约咨询、记录状态、与专业咨询师持续沟通。
          我们希望把每一次进入，都变成一次更安心的开始。
        </p>
      </div>

      <div class="showcase-panels">
        <article class="feature-panel primary">
          <span>给来访者</span>
          <strong>从测评、预约到沟通，获得连续支持</strong>
          <p>支持心理测评、咨询预约与日常沟通记录，让求助路径更清晰，也更容易坚持下去。</p>
        </article>
        <article class="feature-panel">
          <span>给咨询师</span>
          <strong>保留专业登记入口，完善个人服务信息</strong>
          <p>咨询师可以在注册时同步填写专业资料，帮助平台建立更完整、可信的咨询支持信息。</p>
        </article>
        <article class="feature-panel soft">
          <span>陪伴方式</span>
          <strong>关注你的状态变化，也尊重你的节奏</strong>
          <p>无论是先看看测评结果，还是先找一位适合的咨询师，都可以按照你觉得舒服的方式开始。</p>
        </article>
      </div>
    </section>

    <section class="auth-panel-shell">
      <div class="auth-card">
        <div class="auth-card-top">
          <div>
            <p class="auth-eyebrow">心理支持入口</p>
            <h2>{{ activeMode === 'login' ? '欢迎回来' : '创建新账户' }}</h2>
            <p class="auth-subtitle">
              {{ activeMode === 'login'
                ? '登录后可以继续查看测评、预约记录和沟通内容。'
                : '支持普通用户注册，也支持咨询师在注册时同步完成专业信息登记。' }}
            </p>
          </div>
          <div class="auth-switcher">
            <button
              type="button"
              class="switcher-item"
              :class="{ active: activeMode === 'login' }"
              @click="setMode('login')"
            >
              登录
            </button>
            <button
              type="button"
              class="switcher-item"
              :class="{ active: activeMode === 'register' }"
              @click="setMode('register')"
            >
              注册
            </button>
          </div>
        </div>

        <transition name="auth-panel" mode="out-in">
          <el-form
            v-if="activeMode === 'login'"
            key="login"
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="top"
            class="auth-form"
            @submit.prevent
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                clearable
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
                size="large"
              />
            </el-form-item>

            <div class="form-footnote">
              <span>如果你已经建立账户，可以从这里继续进入自己的支持记录。</span>
            </div>

            <el-button
              type="primary"
              size="large"
              class="auth-submit"
              :loading="loginLoading"
              @click="handleLogin"
            >
              登录并进入平台
            </el-button>
          </el-form>

          <el-form
            v-else
            key="register"
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            class="auth-form auth-form-register"
            @submit.prevent
          >
            <el-form-item label="账号类型" prop="role">
              <div class="role-grid">
                <button
                  type="button"
                  class="role-card"
                  :class="{ active: registerForm.role === 'USER' }"
                  @click="registerForm.role = 'USER'"
                >
                  <strong>普通用户</strong>
                  <span>用于测评、预约咨询、在线沟通和内容阅读。</span>
                </button>
                <button
                  type="button"
                  class="role-card"
                  :class="{ active: registerForm.role === 'COUNSELOR' }"
                  @click="registerForm.role = 'COUNSELOR'"
                >
                  <strong>咨询师</strong>
                  <span>用于入驻平台、维护专业档案和处理来访预约。</span>
                </button>
              </div>
            </el-form-item>

            <div class="field-grid two">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" clearable />
              </el-form-item>
              <el-form-item label="昵称" prop="nickname">
                <el-input v-model="registerForm.nickname" placeholder="请输入昵称" size="large" clearable />
              </el-form-item>
            </div>

            <div class="field-grid two">
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="registerForm.email" placeholder="请输入邮箱" size="large" clearable />
              </el-form-item>
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="registerForm.phone" placeholder="请输入手机号" size="large" clearable />
              </el-form-item>
            </div>

            <div class="field-grid two">
              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  show-password
                  placeholder="至少 6 位，建议包含字母和数字"
                  size="large"
                />
              </el-form-item>
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  show-password
                  placeholder="请再次输入密码"
                  size="large"
                />
              </el-form-item>
            </div>

            <transition name="counselor-fields">
              <div v-if="isCounselor" class="counselor-section">
                <div class="section-heading">
                  <span>咨询师专业信息登记</span>
                  <p>以下信息会在注册时一并保存，用于展示咨询背景、擅长方向与服务说明。</p>
                </div>

                <div class="field-grid two">
                  <el-form-item label="职称" prop="title">
                    <el-input v-model="registerForm.title" placeholder="如国家二级心理咨询师" size="large" clearable />
                  </el-form-item>
                  <el-form-item label="擅长方向" prop="specialties">
                    <el-input v-model="registerForm.specialties" placeholder="如焦虑干预、婚恋关系" size="large" clearable />
                  </el-form-item>
                </div>

                <div class="field-grid two">
                  <el-form-item label="从业年限" prop="yearsOfExperience">
                    <el-input-number
                      v-model="registerForm.yearsOfExperience"
                      :min="0"
                      :max="50"
                      size="large"
                      class="full-input"
                    />
                  </el-form-item>
                  <el-form-item label="咨询价格（元/小时）" prop="pricePerHour">
                    <el-input-number
                      v-model="registerForm.pricePerHour"
                      :min="0"
                      :max="5000"
                      :step="50"
                      size="large"
                      class="full-input"
                    />
                  </el-form-item>
                </div>

                <el-form-item label="专业简介" prop="introduction">
                  <el-input
                    v-model="registerForm.introduction"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入专业背景、服务对象、咨询风格和优势领域"
                    resize="none"
                  />
                </el-form-item>
              </div>
            </transition>

            <div class="form-footnote">
              <span>{{ isCounselor ? '完成注册后，系统会同步创建咨询师专业档案。' : '注册成功后，你可以立即登录并开始使用。' }}</span>
            </div>

            <el-button
              type="primary"
              size="large"
              class="auth-submit"
              :loading="registerLoading"
              @click="handleRegister"
            >
              {{ isCounselor ? '提交咨询师登记' : '创建用户账户' }}
            </el-button>
          </el-form>
        </transition>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import { useUserStore } from '@/stores/user'
import type { RegisterPayload } from '@/types'

type AuthMode = 'login' | 'register'

type RegisterFormState = RegisterPayload & {
  confirmPassword: string
}

const router = useRouter()
const userStore = useUserStore()

const activeMode = ref<AuthMode>('login')
const loginLoading = ref(false)
const registerLoading = ref(false)
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

const registerForm = reactive<RegisterFormState>({
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: '',
  role: 'USER',
  title: '',
  specialties: '',
  yearsOfExperience: 0,
  introduction: '',
  pricePerHour: 300,
  confirmPassword: ''
})

const isCounselor = computed(() => registerForm.role === 'COUNSELOR')

const validatePhone = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请输入手机号'))
    return
  }
  if (!/^1\d{10}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
    return
  }
  callback()
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
    return
  }
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const validateCounselorField = (message: string) => {
  return (_rule: unknown, value: unknown, callback: (error?: Error) => void) => {
    if (!isCounselor.value) {
      callback()
      return
    }
    if (value === undefined || value === null || String(value).trim() === '') {
      callback(new Error(message))
      return
    }
    callback()
  }
}

const validateCounselorNumber = (message: string) => {
  return (_rule: unknown, value: unknown, callback: (error?: Error) => void) => {
    if (!isCounselor.value) {
      callback()
      return
    }
    if (typeof value !== 'number' || Number.isNaN(value) || value < 0) {
      callback(new Error(message))
      return
    }
    callback()
  }
}

const loginRules: FormRules<typeof loginForm> = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules: FormRules<RegisterFormState> = {
  role: [{ required: true, message: '请选择账号类型', trigger: 'change' }],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '用户名长度需为 4-20 位', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  phone: [{ validator: validatePhone, trigger: ['blur', 'change'] }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: ['blur', 'change'] }],
  title: [{ validator: validateCounselorField('请输入职称'), trigger: 'blur' }],
  specialties: [{ validator: validateCounselorField('请输入擅长方向'), trigger: 'blur' }],
  yearsOfExperience: [{ validator: validateCounselorNumber('请输入从业年限'), trigger: 'change' }],
  pricePerHour: [{ validator: validateCounselorNumber('请输入咨询价格'), trigger: 'change' }],
  introduction: [{ validator: validateCounselorField('请输入专业简介'), trigger: 'blur' }]
}

const setMode = (mode: AuthMode) => {
  activeMode.value = mode
}

const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    loginLoading.value = true
    await userStore.login(loginForm)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error((error as Error).message)
  } finally {
    loginLoading.value = false
  }
}

const resetRegisterForm = () => {
  registerForm.username = ''
  registerForm.password = ''
  registerForm.confirmPassword = ''
  registerForm.nickname = ''
  registerForm.email = ''
  registerForm.phone = ''
  registerForm.role = 'USER'
  registerForm.title = ''
  registerForm.specialties = ''
  registerForm.yearsOfExperience = 0
  registerForm.introduction = ''
  registerForm.pricePerHour = 300
}

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    registerLoading.value = true
    const payload: RegisterPayload = {
      username: registerForm.username,
      password: registerForm.password,
      nickname: registerForm.nickname,
      email: registerForm.email,
      phone: registerForm.phone,
      role: registerForm.role,
      title: registerForm.title,
      specialties: registerForm.specialties,
      yearsOfExperience: registerForm.yearsOfExperience,
      introduction: registerForm.introduction,
      pricePerHour: registerForm.pricePerHour
    }
    await http.post<null>('/auth/register', payload)
    ElMessage.success(isCounselor.value ? '咨询师登记成功，请登录' : '注册成功，请登录')
    loginForm.username = registerForm.username
    loginForm.password = registerForm.password
    resetRegisterForm()
    activeMode.value = 'login'
  } catch (error) {
    ElMessage.error((error as Error).message)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  --auth-bg: #f4efe6;
  --auth-panel: rgba(255, 255, 255, 0.72);
  --auth-border: rgba(29, 63, 53, 0.1);
  --auth-text: #19352f;
  --auth-muted: rgba(25, 53, 47, 0.66);
  --auth-strong: #10342d;
  --auth-primary: #174f43;
  --auth-primary-soft: rgba(23, 79, 67, 0.08);
  --auth-shadow: 0 30px 80px rgba(32, 55, 48, 0.14);

  position: relative;
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(420px, 560px);
  gap: 44px;
  padding: 32px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.85), transparent 34%),
    linear-gradient(135deg, #f6f0e8 0%, #efe9df 45%, #e7eee8 100%);
}

.auth-backdrop {
  position: absolute;
  border-radius: 999px;
  filter: blur(18px);
  pointer-events: none;
}

.auth-backdrop-left {
  top: -120px;
  left: -120px;
  width: 360px;
  height: 360px;
  background: rgba(136, 210, 182, 0.2);
}

.auth-backdrop-right {
  right: -100px;
  bottom: -80px;
  width: 320px;
  height: 320px;
  background: rgba(224, 193, 145, 0.22);
}

.auth-showcase,
.auth-panel-shell {
  position: relative;
  z-index: 1;
}

.auth-showcase {
  display: grid;
  align-content: center;
  gap: 28px;
  min-width: 0;
  padding: 20px 8px;
}

.showcase-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  padding: 10px 16px;
  border: 1px solid rgba(23, 79, 67, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.55);
  color: var(--auth-primary);
  font-size: 13px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  backdrop-filter: blur(16px);
}

.showcase-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #58b08a, #1c6e5c);
  box-shadow: 0 0 0 6px rgba(88, 176, 138, 0.12);
}

.showcase-copy h1 {
  max-width: 720px;
  margin: 10px 0 18px;
  color: var(--auth-strong);
  font-size: clamp(46px, 5.2vw, 78px);
  line-height: 1.04;
  letter-spacing: -0.04em;
}

.showcase-kicker {
  margin: 0;
  color: #6d857c;
  font-size: 14px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.showcase-text {
  max-width: 620px;
  margin: 0;
  color: var(--auth-muted);
  font-size: 17px;
  line-height: 1.9;
}

.showcase-panels {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  max-width: 920px;
}

.feature-panel {
  padding: 22px 22px 20px;
  border: 1px solid rgba(23, 79, 67, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.56);
  box-shadow: 0 18px 50px rgba(31, 55, 48, 0.07);
  backdrop-filter: blur(16px);
}

.feature-panel.primary {
  background: linear-gradient(180deg, rgba(24, 82, 70, 0.9), rgba(22, 62, 54, 0.96));
  border-color: transparent;
  box-shadow: 0 22px 60px rgba(19, 58, 50, 0.24);
}

.feature-panel.soft {
  background: linear-gradient(180deg, rgba(255, 252, 247, 0.9), rgba(250, 245, 238, 0.82));
}

.feature-panel span {
  display: inline-block;
  margin-bottom: 14px;
  color: #7f958d;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.feature-panel.primary span,
.feature-panel.primary strong,
.feature-panel.primary p {
  color: #f7f4ee;
}

.feature-panel strong {
  display: block;
  margin-bottom: 10px;
  color: var(--auth-text);
  font-size: 20px;
  line-height: 1.4;
}

.feature-panel p {
  margin: 0;
  color: var(--auth-muted);
  line-height: 1.75;
}

.auth-panel-shell {
  display: grid;
  align-items: center;
}

.auth-card {
  padding: 26px;
  border: 1px solid var(--auth-border);
  border-radius: 36px;
  background: var(--auth-panel);
  box-shadow: var(--auth-shadow);
  backdrop-filter: blur(24px);
}

.auth-card-top {
  display: grid;
  gap: 18px;
  margin-bottom: 24px;
}

.auth-eyebrow {
  margin: 0 0 10px;
  color: #728981;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.auth-card-top h2 {
  margin: 0;
  color: var(--auth-strong);
  font-size: 34px;
  letter-spacing: -0.03em;
}

.auth-subtitle {
  margin: 10px 0 0;
  color: var(--auth-muted);
  line-height: 1.8;
}

.auth-switcher {
  display: inline-grid;
  grid-template-columns: repeat(2, 1fr);
  width: fit-content;
  padding: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 0 0 1px rgba(23, 79, 67, 0.08);
}

.switcher-item {
  min-width: 92px;
  padding: 11px 18px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #6e857e;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.24s ease, color 0.24s ease, box-shadow 0.24s ease;
}

.switcher-item.active {
  background: linear-gradient(135deg, #1d5d50, #143f37);
  color: #fff;
  box-shadow: 0 10px 22px rgba(22, 63, 54, 0.22);
}

.auth-form {
  display: grid;
  gap: 4px;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.auth-form :deep(.el-form-item__label) {
  padding-bottom: 8px;
  color: #304842;
  font-size: 13px;
  font-weight: 600;
}

.auth-form :deep(.el-input__wrapper),
.auth-form :deep(.el-textarea__inner),
.auth-form :deep(.el-input-number) {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: inset 0 0 0 1px rgba(23, 79, 67, 0.08);
  transition: box-shadow 0.22s ease, transform 0.22s ease, background-color 0.22s ease;
}

.auth-form :deep(.el-input__wrapper:hover),
.auth-form :deep(.el-textarea__inner:hover),
.auth-form :deep(.el-input-number:hover) {
  box-shadow: inset 0 0 0 1px rgba(23, 79, 67, 0.18);
}

.auth-form :deep(.is-focus .el-input__wrapper),
.auth-form :deep(.el-textarea__inner:focus),
.auth-form :deep(.el-input-number.is-controls-right) {
  box-shadow: 0 0 0 4px rgba(27, 95, 79, 0.1), inset 0 0 0 1px rgba(22, 79, 66, 0.26);
}

.auth-form :deep(.el-input__inner),
.auth-form :deep(.el-textarea__inner) {
  color: var(--auth-text);
}

.auth-form :deep(.el-textarea__inner) {
  padding: 14px 16px;
}

.field-grid {
  display: grid;
  gap: 16px;
}

.field-grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.role-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid rgba(23, 79, 67, 0.08);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--auth-text);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
}

.role-card:hover {
  transform: translateY(-1px);
  border-color: rgba(23, 79, 67, 0.18);
  box-shadow: 0 14px 30px rgba(28, 60, 52, 0.08);
}

.role-card.active {
  border-color: rgba(23, 79, 67, 0.22);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(231, 241, 236, 0.92));
  box-shadow: 0 18px 36px rgba(26, 68, 58, 0.1);
}

.role-card strong {
  font-size: 16px;
}

.role-card span {
  color: var(--auth-muted);
  line-height: 1.7;
}

.counselor-section {
  margin: 4px 0 10px;
  padding: 18px;
  border: 1px solid rgba(23, 79, 67, 0.08);
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(248, 251, 249, 0.9), rgba(255, 255, 255, 0.72));
}

.section-heading {
  margin-bottom: 16px;
}

.section-heading span {
  display: block;
  margin-bottom: 8px;
  color: var(--auth-primary);
  font-size: 15px;
  font-weight: 700;
}

.section-heading p,
.form-footnote {
  margin: 0;
  color: var(--auth-muted);
  font-size: 13px;
  line-height: 1.7;
}

.form-footnote {
  margin-bottom: 18px;
}

.auth-submit {
  width: 100%;
  min-height: 54px;
  border: 0;
  border-radius: 18px;
  background: linear-gradient(135deg, #1e6658, #133f37);
  box-shadow: 0 20px 36px rgba(20, 63, 55, 0.24);
}

.auth-submit :deep(span) {
  font-weight: 700;
  letter-spacing: 0.02em;
}

.full-input {
  width: 100%;
}

.auth-panel-enter-active,
.auth-panel-leave-active,
.counselor-fields-enter-active,
.counselor-fields-leave-active {
  transition: opacity 0.26s ease, transform 0.26s ease;
}

.auth-panel-enter-from,
.auth-panel-leave-to,
.counselor-fields-enter-from,
.counselor-fields-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 1180px) {
  .auth-page {
    grid-template-columns: 1fr;
    gap: 28px;
    padding: 24px;
  }

  .auth-showcase {
    padding: 10px 2px 0;
  }

  .showcase-panels {
    grid-template-columns: 1fr;
    max-width: none;
  }
}

@media (max-width: 760px) {
  .auth-page {
    padding: 16px;
  }

  .auth-card {
    padding: 18px;
    border-radius: 28px;
  }

  .showcase-copy h1 {
    font-size: 40px;
  }

  .showcase-panels,
  .field-grid.two,
  .role-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .showcase-copy h1 {
    font-size: 34px;
  }

  .auth-switcher {
    width: 100%;
  }

  .switcher-item {
    min-width: 0;
  }
}
</style>
