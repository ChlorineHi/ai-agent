<template>
  <div class="login-background">
    <MathFormulaBackground />
    <!-- 登录表单内容 -->
    <!-- <VueParticleAnimation /> -->
    <div id="mouse-follow"></div> <!-- 鼠标跟随光晕 -->
    <div class="login-container">
      <div class="login-header">
        <h1>欢迎登录</h1>
        <p class="subtitle">请使用您的账号密码登录系统</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <div class="input-wrapper">
            <i class="el-icon-user"></i>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              required 
              class="input-field"
              placeholder="请输入您的用户名" 
              :class="{ 'error': usernameError }"
              @focus="clearErrors"
            />
            <span class="error-message" v-if="usernameError">{{ usernameError }}</span>
          </div>
        </div>
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <div class="input-wrapper">
            <i class="el-icon-lock"></i>
            <input 
              :type="showPassword ? 'text' : 'password'"
              id="password" 
              v-model="password" 
              required 
              class="input-field"
              placeholder="请输入您的密码"
              :class="{ 'error': passwordError }"
              @keyup.enter="handleLogin"
              @focus="clearErrors"
            />
            <i 
              :class="showPassword ? 'el-icon-view' : 'el-icon-hide'"
              class="password-toggle"
              @click="showPassword = !showPassword"
              :title="showPassword ? '隐藏密码' : '显示密码'"
            ></i>
            <span class="error-message" v-if="passwordError">{{ passwordError }}</span>
          </div>
        </div>
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe">
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">忘记密码？</a>
        </div>
        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="!isLoading">登录</span>
          <i v-else class="el-icon-loading"></i>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import MathFormulaBackground from '@/components/MathFormulaBackground.vue'

const router = useRouter()
const route = useRoute()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const usernameError = ref('')
const passwordError = ref('')

const clearErrors = () => {
  usernameError.value = ''
  passwordError.value = ''
}

const validateForm = () => {
  let isValid = true
  clearErrors()

  if (!username.value) {
    usernameError.value = '请输入用户名'
    isValid = false
  }

  if (!password.value) {
    passwordError.value = '请输入密码'
    isValid = false
  } else if (password.value.length < 6) {
    passwordError.value = '密码长度不能少于6位'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) return

  try {
    isLoading.value = true
    // 简单的密码验证
    if (password.value === '123456') {
      // 登录成功
      ElMessage.success('登录成功')
      // 存储登录状态
      if (rememberMe.value) {
        localStorage.setItem('username', username.value)
      }
      localStorage.setItem('isLoggedIn', 'true')
      
      // 获取重定向路径或使用默认路径
      const redirectPath = route.query.redirect || '/chat'
      
      // 等待消息显示完成后跳转
      setTimeout(() => {
        router.push(redirectPath)
      }, 500)
    } else {
      ElMessage.error('用户名或密码错误')
      passwordError.value = '密码错误'
    }
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('登录失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const handleForgotPassword = () => {
  ElMessage.info('密码重置功能开发中...')
}
</script>

<style scoped>
.login-background {
  position: relative;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background: #ffffff;
}

.login-container {
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  padding: 40px;
  width: 380px;
  margin: auto;
  border: 1px solid #f0f0f0;
  z-index: 20;
  position: relative;
  transition: transform 0.3s ease;
}

.login-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #1a237e;
  font-size: 28px;
  margin-bottom: 8px;
  font-weight: 600;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-field {
  width: 100%;
  padding: 12px 40px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.input-field:focus {
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.input-field.error {
  border-color: #ff5252;
  background: #fff;
}

.error-message {
  position: absolute;
  left: 0;
  bottom: -20px;
  color: #ff5252;
  font-size: 12px;
}

.input-wrapper i {
  position: absolute;
  left: 12px;
  color: #666;
  font-size: 16px;
}

.password-toggle {
  position: absolute;
  right: 12px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: #1a237e;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.forgot-password {
  color: #667eea;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #1a237e;
  text-decoration: underline;
}

.login-button {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(102, 126, 234, 0.2);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .login-container {
    width: 90%;
    padding: 24px;
  }

  .login-header h1 {
    font-size: 24px;
  }

  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>