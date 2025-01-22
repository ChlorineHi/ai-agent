<template>
  <div class="about-container">
    <!-- 背景动画元素 -->
    <div class="animated-background">
      <div class="gradient-sphere sphere-1" :style="sphere1Style"></div>
      <div class="gradient-sphere sphere-2" :style="sphere2Style"></div>
      <div class="gradient-sphere sphere-3" :style="sphere3Style"></div>
    </div>
    <router-link to="/chat" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回聊天
   </router-link>

    <!-- 网格叠加层 -->
    <div class="grid-overlay"></div>

    <!-- 模糊背景 -->
    <div class="blur-background"></div>

    <!-- 鼠标跟随效果 -->
    <div class="mouse-follower" :style="mouseFollowerStyle"></div>

    <!-- 主要内容 -->
    <div class="about-content" :class="{ 'content-hover': isHovered }">
      <!-- 动态模糊背景 -->
      <div class="blur-background"></div>

      <div class="header-section">
        <div class="logo-icon">
          <el-icon><ChatRound /></el-icon>
        </div>
        <h1 class="title">关于我们的AI助手</h1>
        <p class="subtitle">智能对话，改变未来</p>
      </div>
      
      <div class="intro-section">
        <h2>项目简介</h2>
        <p class="intro-text" :class="{ 'typing': isTyping }">
          <span class="typed-text">{{ displayedText }}</span>
          <span class="cursor" v-show="isTyping"></span>
        </p>
      </div>

      <div class="section fade-in">
        <div class="section-icon">
          <el-icon size="24"><InfoFilled /></el-icon>
        </div>
        <h2>主要功能</h2>
        <div class="features-grid">
          <div
            v-for="(feature, index) in features"
            :key="index"
            class="feature-card"
            :class="{ 'hovered': feature.isHovered, 'activated': feature.isActivated }"
            @mouseenter="handleFeatureHover(index, true)"
            @mouseleave="handleFeatureHover(index, false)"
          >
            <div class="feature-icon">
              <el-icon :size="32">
                <component :is="getIcon(feature.iconName)" />
              </el-icon>
            </div>
            <div class="feature-content">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="tech-section">
        <h2 class="section-title">
          <span class="title-icon">🚀</span>
          技术特点
          <div class="title-underline"></div>
        </h2>
        <div class="tech-grid">
          <div
            v-for="(feature, index) in techFeatures"
            :key="index"
            class="tech-card"
            :class="{ 'visible': techVisible[index] }"
            :ref="el => techRefs[index] = el"
            @mouseenter="handleTechHover(index, true)"
            @mouseleave="handleTechHover(index, false)"
          >
            <div class="tech-content">
              <div class="tech-icon-wrapper">
                <span class="tech-icon">{{ feature.icon }}</span>
                <div class="icon-background"></div>
              </div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
            <div class="tech-card-background"></div>
            <div class="tech-card-border"></div>
          </div>
        </div>
      </div>

      <div class="section contact-section fade-in">
        <div class="section-icon">
          <el-icon size="24"><Message /></el-icon>
        </div>
        <h2>联系我们</h2>
        <div class="contact-content">
          <p>如果您有任何问题或建议，欢迎通过以下方式联系我们：</p>
          <div class="contact-methods">
            <button class="contact-button" @click="handleEmailClick">
              <el-icon><Message /></el-icon>
              联系我们
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 邮件对话框 -->
  <el-dialog
    v-model="showEmailDialog"
    title="发送邮件"
    width="500px"
    class="email-dialog"
    :close-on-click-modal="false"
  >
    <el-form
      ref="emailFormRef"
      :model="emailForm"
      :rules="emailRules"
      label-position="top"
    >
      <el-form-item label="您的姓名" prop="name">
        <el-input
          v-model="emailForm.name"
          placeholder="请输入您的姓名"
          :disabled="isSubmitting"
        />
      </el-form-item>
      
      <el-form-item label="邮箱地址" prop="email">
        <el-input
          v-model="emailForm.email"
          placeholder="请输入您的邮箱地址"
          :disabled="isSubmitting"
        />
      </el-form-item>
      
      <el-form-item label="邮件主题" prop="subject">
        <el-input
          v-model="emailForm.subject"
          placeholder="请输入邮件主题"
          :disabled="isSubmitting"
        />
      </el-form-item>
      
      <el-form-item label="邮件内容" prop="message">
        <el-input
          v-model="emailForm.message"
          type="textarea"
          rows="4"
          placeholder="请输入邮件内容"
          :disabled="isSubmitting"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button
        class="submit-button"
        :loading="isSubmitting"
        @click="handleEmailSubmit"
      >
        {{ isSubmitting ? '发送中...' : '发送邮件' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, markRaw, shallowRef } from 'vue'
import { 
  InfoFilled, Star, Connection, Message, ChatLineRound,
  Document, Lock, Refresh, Monitor, ChatRound,ArrowLeft
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const isHovered = ref(false)
const mousePosition = ref({ x: 0, y: 0 })
let rafId = null
let lastMouseX = 0
let lastMouseY = 0

// 使用防抖处理鼠标移动
const handleMouseMove = (event) => {
  lastMouseX = event.clientX
  lastMouseY = event.clientY
  
  if (!rafId) {
    rafId = requestAnimationFrame(updateMousePosition)
  }
}

// 使用 requestAnimationFrame 更新位置
const updateMousePosition = () => {
  mousePosition.value = {
    x: lastMouseX,
    y: lastMouseY
  }
  rafId = null
}

// 计算鼠标跟随样式
const mouseFollowerStyle = computed(() => {
  const { x, y } = mousePosition.value
  return {
    background: `radial-gradient(600px circle at ${x}px ${y}px, 
                 rgba(var(--el-color-primary-rgb), 0.15),
                 transparent 40%)`
  }
})

// 优化计算球体位置
const calculateSpherePosition = (x, y, factor) => {
  const centerX = window.innerWidth / 2
  const centerY = window.innerHeight / 2
  return {
    transform: `translate3d(${(x - centerX) / factor}px, ${(y - centerY) / factor}px, 0)`
  }
}

// 使用 transform3d 加速
const sphere1Style = computed(() => calculateSpherePosition(mousePosition.value.x, mousePosition.value.y, 20))
const sphere2Style = computed(() => calculateSpherePosition(mousePosition.value.x, mousePosition.value.y, -30))
const sphere3Style = computed(() => calculateSpherePosition(mousePosition.value.x, mousePosition.value.y, 25))

// 清理动画帧
onUnmounted(() => {
  if (rafId) {
    cancelAnimationFrame(rafId)
  }
})

// 使用 shallowRef 来存储图标组件
const icons = shallowRef(markRaw({
  InfoFilled: InfoFilled,
  Star: Star,
  Connection: Connection,
  Message: Message,
  ChatLineRound: ChatLineRound,
  Document: Document,
  Lock: Lock,
  Refresh: Refresh,
  Monitor: Monitor,
  ChatRound: ChatRound
}))

// 功能特点数据
const features = ref([
  {
    title: '智能对话',
    description: '基于先进的AI模型，提供智能、自然的对话体验',
    iconName: 'ChatRound',
    isHovered: false,
    isActivated: false
  },
  {
    title: '实时响应',
    description: '快速的响应速度，提供流畅的用户体验',
    iconName: 'Monitor',
    isHovered: false,
    isActivated: false
  },
  {
    title: '安全可靠',
    description: '采用先进的安全措施，保护用户数据和隐私',
    iconName: 'Lock',
    isHovered: false,
    isActivated: false
  },
  {
    title: '持续更新',
    description: '定期更新模型和功能，持续提供最佳体验',
    iconName: 'Refresh',
    isHovered: false,
    isActivated: false
  }
])

// 获取图标组件
const getIcon = (name) => {
  return icons.value[name]
}

const techFeatures = ref([
  {
    title: "智能对话引擎",
    description: "基于最新的大语言模型，提供流畅自然的对话体验",
    icon: "🤖",
    color: "rgb(var(--el-color-primary-rgb))",
    delay: 0
  },
  {
    title: "实时响应系统",
    description: "毫秒级的响应速度，支持流式输出和多轮对话",
    icon: "⚡",
    color: "rgb(var(--el-color-success-rgb))",
    delay: 200
  },
  {
    title: "知识图谱集成",
    description: "融合专业领域知识，提供精准的专业解答",
    icon: "🧠",
    color: "rgb(var(--el-color-warning-rgb))",
    delay: 400
  },
  {
    title: "多模态交互",
    description: "支持文本、语音等多种交互方式，打造沉浸式体验",
    icon: "🎯",
    color: "rgb(var(--el-color-danger-rgb))",
    delay: 600
  }
])

const techRefs = ref([])
const techVisible = ref(new Array(4).fill(false))

// 监听技术特点的可见性
onMounted(() => {
  nextTick(() => {
    const techObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const index = techRefs.value.findIndex(ref => ref === entry.target)
        if (index !== -1 && entry.isIntersecting) {
          setTimeout(() => {
            techVisible.value[index] = true
          }, techFeatures.value[index].delay)
        }
      })
    }, {
      threshold: 0.3,
      rootMargin: '0px'
    })

    // 确保所有引用都已经设置
    techRefs.value.forEach(ref => {
      if (ref) {
        techObserver.observe(ref)
      }
    })

    // 清理函数
    return () => {
      techRefs.value.forEach(ref => {
        if (ref) {
          techObserver.unobserve(ref)
        }
      })
    }
  })
})

const handleFeatureHover = (index, isEntering) => {
  const feature = features.value[index]
  feature.isHovered = isEntering
  
  if (isEntering) {
    feature.isActivated = true
    const centerX = window.innerWidth / 2
    const centerY = window.innerHeight / 2
    
    // 根据特性位置调整球体动画
    switch(index) {
      case 0: // 多轮对话
        mousePosition.value = { x: centerX - 200, y: centerY - 100 }
        break
      case 1: // 上下文连贯
        mousePosition.value = { x: centerX + 200, y: centerY }
        break
      case 2: // 流畅对话
        mousePosition.value = { x: centerX, y: centerY + 150 }
        break
    }
  }
}

const handleTechHover = (index, isEntering) => {
  const card = techRefs.value[index]
  if (!card) return

  if (isEntering) {
    card.style.transform = 'translateY(-5px)'
    card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.1)'
  } else {
    card.style.transform = 'translateY(0)'
    card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.05)'
  }
}

// 检查是否所有特性都已激活
const allFeaturesActivated = computed(() => {
  return features.value.every(feature => feature.isActivated)
})

// 邮件发送功能
const showEmailDialog = ref(false)
const emailForm = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})
const emailFormRef = ref(null)
const isSubmitting = ref(false)

const emailRules = {
  name: [
    { required: true, message: '请输入您的姓名', trigger: 'blur' },
    { min: 2, message: '姓名至少需要2个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '请输入邮件主题', trigger: 'blur' },
    { min: 5, message: '主题至少需要5个字符', trigger: 'blur' }
  ],
  message: [
    { required: true, message: '请输入邮件内容', trigger: 'blur' },
    { min: 10, message: '内容至少需要10个字符', trigger: 'blur' }
  ]
}

const handleEmailClick = () => {
  showEmailDialog.value = true
  // 触发特殊的背景动画
  mousePosition.value = {
    x: window.innerWidth / 2,
    y: window.innerHeight / 2
  }
}

const handleEmailSubmit = async () => {
  if (!emailFormRef.value) return
  
  try {
    await emailFormRef.value.validate()
    isSubmitting.value = true
    
    // 这里添加实际的邮件发送逻辑
    await new Promise(resolve => setTimeout(resolve, 1500)) // 模拟发送
    
    ElMessage({
      type: 'success',
      message: '邮件发送成功！我们会尽快回复您。',
      duration: 3000
    })
    
    showEmailDialog.value = false
    emailForm.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  } catch (error) {
    ElMessage({
      type: 'error',
      message: '请检查表单信息是否填写正确',
      duration: 3000
    })
  } finally {
    isSubmitting.value = false
  }
}

// 项目简介文本
const introText = "这是一个基于先进AI技术的智能对话助手，能够帮助用户解决各种问题，提供智能化的对话服务。结合最新的大语言模型技术，为您带来更智能、更自然的对话体验。"
const displayedText = ref('')
const isTyping = ref(false)
let currentIndex = 0
let typingTimer = null

const startTypingAnimation = () => {
  if (isTyping.value) return
  
  isTyping.value = true
  displayedText.value = ''
  currentIndex = 0
  
  const typeNextChar = () => {
    if (currentIndex < introText.length) {
      displayedText.value += introText[currentIndex]
      currentIndex++
      
      // 随机延迟，模拟真实打字效果
      const delay = Math.random() * 50 + 30 // 30-80ms
      typingTimer = setTimeout(typeNextChar, delay)
    } else {
      isTyping.value = false
    }
  }
  
  typeNextChar()
}

// 清理定时器
onUnmounted(() => {
  if (typingTimer) {
    clearTimeout(typingTimer)
  }
})

// 监听可见性变化
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      startTypingAnimation()
    }
  })
}, {
  threshold: 0.5
})

onMounted(() => {
  const introElement = document.querySelector('.intro-text')
  if (introElement) {
    observer.observe(introElement)
  }
})
</script>

<style scoped>

.back-button {
  position: fixed;
  left: 20px;
  top: 10%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(99, 125, 255, 0.1), rgba(162, 89, 255, 0.2));
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.5px;
}

.back-button:hover {
  background: linear-gradient(135deg, rgba(99, 125, 255, 0.2), rgba(162, 89, 255, 0.3));
  transform: translateY(-50%) translateX(5px);
  box-shadow: 0 6px 20px rgba(99, 125, 255, 0.2);
  color: #ffffff;
}

.back-button .el-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.back-button:hover .el-icon {
  transform: translateX(-3px);
}


.about-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background-color: var(--el-bg-color);
}

.about-content {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  border-radius: 16px;
  transform: translateZ(0);
  backface-visibility: hidden;
  will-change: transform;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-section {
  text-align: center;
  margin-bottom: 4rem;
  animation: fadeInDown 0.8s ease-out;
}

.logo-icon {
  font-size: 80px;
  margin-bottom: 1.5rem;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  width: 120px;
  height: 120px;
  border-radius: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(var(--el-color-primary-rgb), 0.2);
}

.title {
  color: var(--el-text-color-primary);
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(120deg, var(--el-color-primary), var(--el-color-success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--el-text-color-secondary);
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.intro-section {
  margin-bottom: 4rem;
  position: relative;
  padding-top: 2rem;
  opacity: 0;
  animation: fadeInUp 0.8s ease-out forwards;
}

.intro-section:nth-child(2) { animation-delay: 0.2s; }
.intro-section:nth-child(3) { animation-delay: 0.4s; }
.intro-section:nth-child(4) { animation-delay: 0.6s; }
.intro-section:nth-child(5) { animation-delay: 0.8s; }

.intro-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--el-text-color-primary);
  position: relative;
  padding: 2rem;
  background: rgba(var(--el-color-primary-rgb), 0.05);
  border-radius: 12px;
  margin: 2rem 0;
  transition: all 0.3s ease;
}

.intro-text:hover {
  background: rgba(var(--el-color-primary-rgb), 0.1);
}

.typed-text {
  display: inline;
  white-space: pre-wrap;
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: var(--el-color-primary);
  margin-left: 2px;
  vertical-align: middle;
  animation: blink 0.7s infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

/* 打字机效果的渐变背景 */
.typing {
  background: linear-gradient(
    120deg,
    rgba(var(--el-color-primary-rgb), 0.05) 0%,
    rgba(var(--el-color-success-rgb), 0.05) 100%
  );
  border: 1px solid rgba(var(--el-color-primary-rgb), 0.1);
  box-shadow: 0 4px 12px rgba(var(--el-color-primary-rgb), 0.05);
}

/* 添加鼠标悬停效果 */
.typing:hover {
  background: linear-gradient(
    120deg,
    rgba(var(--el-color-primary-rgb), 0.1) 0%,
    rgba(var(--el-color-success-rgb), 0.1) 100%
  );
  box-shadow: 0 8px 24px rgba(var(--el-color-primary-rgb), 0.1);
}

.section {
  margin-bottom: 4rem;
  position: relative;
  padding-top: 2rem;
  opacity: 0;
  animation: fadeInUp 0.8s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.2s; }
.section:nth-child(3) { animation-delay: 0.4s; }
.section:nth-child(4) { animation-delay: 0.6s; }
.section:nth-child(5) { animation-delay: 0.8s; }

.section-icon {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%) translateY(-50%);
  background: var(--el-bg-color);
  padding: 1rem;
  border-radius: 50%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  color: var(--el-color-primary);
}

h2 {
  color: var(--el-text-color-primary);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.card {
  background: var(--el-bg-color-overlay);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.feature-card {
  position: relative;
  padding: 1.5rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(var(--el-color-primary-rgb), 0.15),
    transparent 150px
  );
  opacity: 0;
  transition: opacity 0.5s ease;
}

.feature-card:hover::before,
.feature-card[data-activated="true"]::before {
  opacity: 1;
}

.feature-card:hover,
.feature-card[data-activated="true"] {
  transform: translateY(-5px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2rem;
  color: var(--el-color-primary);
  margin-bottom: 1rem;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.7;
}

.feature-card:hover .feature-icon,
.feature-card[data-activated="true"] .feature-icon {
  transform: scale(1.2);
  opacity: 1;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  background: linear-gradient(
    135deg,
    var(--el-color-primary) 0%,
    var(--el-color-success) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover .feature-title,
.feature-card[data-activated="true"] .feature-title {
  opacity: 1;
  transform: translateY(0);
}

.feature-description {
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover .feature-description,
.feature-card[data-activated="true"] .feature-description {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.1s;
}

.tech-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--el-bg-color-overlay);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tech-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.tech-icon {
  padding: 1rem;
  border-radius: 12px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.tech-content h4 {
  margin: 0 0 0.5rem;
  color: var(--el-text-color-primary);
}

.tech-content p {
  margin: 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.contact-section {
  text-align: center;
}

.contact-content {
  max-width: 600px;
  margin: 0 auto;
}

.contact-methods {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.contact-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  background: linear-gradient(
    135deg,
    var(--el-color-primary) 0%,
    var(--el-color-success) 100%
  );
  color: white;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.contact-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(var(--el-color-primary-rgb), 0.3);
}

.contact-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    45deg,
    transparent 0%,
    rgba(255, 255, 255, 0.2) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.contact-button:hover::before {
  transform: translateX(100%);
}

.tech-section {
  padding: 6rem 0;
  position: relative;
  background: linear-gradient(
    180deg,
    transparent,
    rgba(var(--el-color-primary-rgb), 0.05) 50%,
    transparent
  );
  margin: 2rem 0;
  width: 100%;
}

.section-title {
  text-align: center;
  margin-bottom: 4rem;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 2.5rem;
  color: var(--el-text-color-primary);
}

.title-icon {
  font-size: 2.5rem;
  animation: float 3s ease-in-out infinite;
}

.title-underline {
  position: absolute;
  bottom: -1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--el-color-primary) 50%,
    transparent
  );
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.5rem;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.tech-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  transform: translateY(50px) rotateX(10deg);
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
}

.tech-card.visible {
  transform: translateY(0) rotateX(0);
  opacity: 1;
}

.tech-content {
  position: relative;
  z-index: 2;
}

.tech-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tech-icon {
  font-size: 3rem;
  z-index: 2;
}

.icon-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(var(--el-color-primary-rgb), 0.1),
    rgba(var(--el-color-success-rgb), 0.1)
  );
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.tech-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  background: linear-gradient(
    135deg,
    var(--el-color-primary),
    var(--el-color-success)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tech-card p {
  color: var(--el-text-color-secondary);
  line-height: 1.8;
  font-size: 1.1rem;
}

.tech-card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(var(--el-color-primary-rgb), 0.05),
    rgba(var(--el-color-success-rgb), 0.05)
  );
  opacity: 0;
  transition: all 0.3s ease;
}

.tech-card:hover .tech-card-background {
  opacity: 1;
}

.tech-card-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(
    135deg,
    var(--el-color-primary),
    var(--el-color-success)
  );
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.tech-card:hover .tech-card-border {
  opacity: 1;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

@media (max-width: 768px) {
  .tech-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .tech-card {
    margin: 1rem 0;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

/* 添加卡片出现动画的延迟 */
.tech-card:nth-child(1) { transition-delay: 0ms; }
.tech-card:nth-child(2) { transition-delay: 200ms; }
.tech-card:nth-child(3) { transition-delay: 400ms; }
.tech-card:nth-child(4) { transition-delay: 600ms; }

.animated-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: -2;
  background: linear-gradient(to bottom right, 
    var(--el-color-primary-light-9) 0%,
    var(--el-color-success-light-9) 100%);
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000;
  will-change: transform;
}

.mouse-follower {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 1;
  transition: background 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  mix-blend-mode: plus-lighter;
  will-change: background;
  transform: translateZ(0);
}

.gradient-sphere {
  position: fixed;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.6;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  pointer-events: none;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.sphere-1 {
  width: 800px;
  height: 800px;
  background: radial-gradient(circle at 30% 30%, 
    var(--el-color-primary-light-3),
    transparent);
  top: -20%;
  left: -10%;
  animation: sphereFloat 20s infinite cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: -5s;
}

.sphere-2 {
  width: 1000px;
  height: 1000px;
  background: radial-gradient(circle at 70% 70%, 
    var(--el-color-success-light-3),
    transparent);
  top: 30%;
  right: -20%;
  animation: sphereFloat 25s infinite cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: -10s;
}

.sphere-3 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle at 50% 50%, 
    var(--el-color-warning-light-3),
    transparent);
  bottom: -10%;
  left: 20%;
  animation: sphereFloat 30s infinite cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: -15s;
}

.grid-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.3;
  z-index: -1;
}

.blur-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(80px);
  z-index: 0;
  opacity: 0.5;
  transform: translateZ(0);
}

@keyframes sphereFloat {
  0%, 100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, 30px, 0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(var(--el-color-primary-rgb), 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(var(--el-color-primary-rgb), 0.5);
  }
}

.feature-icon-chat { color: #409EFF; }
.feature-icon-context { color: #67C23A; }
.feature-icon-response { color: #E6A23C; }
.feature-icon-security { color: #F56C6C; }

/* Vue 过渡动画 */
.feature-list-enter-active,
.feature-list-leave-active,
.tech-list-enter-active,
.tech-list-leave-active {
  transition: all 0.5s ease;
}

.feature-list-enter-from,
.feature-list-leave-to,
.tech-list-enter-from,
.tech-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about-container {
    padding: 1rem;
  }

  .about-content {
    padding: 2rem;
  }

  .title {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .tech-list {
    grid-template-columns: 1fr;
  }

  .contact-methods {
    flex-direction: column;
  }

  .logo-icon {
    font-size: 60px;
    width: 100px;
    height: 100px;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .about-content {
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  }

  .tech-icon {
    background: var(--el-color-primary-light-3);
  }

  .logo-icon {
    background: var(--el-color-primary-light-3);
  }
}
</style>
