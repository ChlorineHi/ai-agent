<template>
  <div class="chat-animals">
    <!-- 躺着的小狗 -->
    <div class="animal dog" 
         @click="toggleModePanel" 
         :class="{ 'clickable': true, 'active': showModePanel }">
      <div class="dog-ears">
        <div class="ear-left"></div>
        <div class="ear-right"></div>
      </div>
      <div class="dog-face">
        <div class="eyes">
          <div class="eye left"></div>
          <div class="eye right"></div>
        </div>
        <div class="nose"></div>
        <div class="mouth"></div>
      </div>
      <div class="dog-body">
        <div class="belly"></div>
        <div class="legs">
          <div class="leg front"></div>
          <div class="leg back"></div>
        </div>
        <div class="tail"></div>
      </div>
    </div>

    <!-- 模式选择面板 -->
    <transition name="slide-fade">
      <div v-if="showModePanel" class="mode-panel">
        <div class="panel-header">
          <div class="header-left">
            <span>选择回答模式</span>
            <el-button
              class="help-btn"
              type="text"
              @click.stop="showHelpPanel = true"
            >
              <i class="el-icon-question"></i>
              <span>什么是问答模式?</span>
            </el-button>
          </div>
          <el-icon class="close-icon" @click.stop="showModePanel = false">
            <i class="el-icon-close"></i>
          </el-icon>
        </div>
        <div class="mode-options">
          <div class="mode-option" 
               v-for="mode in modes" 
               :key="mode.value"
               :class="{ 'active': currentMode === mode.value }"
               @click="selectMode(mode)">
            <div class="mode-icon">
              <i :class="mode.icon"></i>
            </div>
            <div class="mode-info">
              <div class="mode-title">{{ mode.label }}</div>
              <div class="mode-desc">{{ mode.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 添加遮罩层和关闭提示 -->
    <transition name="fade">
      <div v-if="showHelpPanel" class="help-overlay" @click="showHelpPanel = false">
        <div class="help-panel" @click.stop>
          <div class="help-header">
            <span>问答模式说明</span>
            <div class="close-tip">
              <span>点击空白处关闭</span>
              <el-icon class="close-icon" @click.stop="showHelpPanel = false">
                <i class="el-icon-close"></i>
              </el-icon>
            </div>
          </div>
          <div class="help-content">
            <div v-for="mode in modes" :key="mode.value" class="help-item">
              <div class="help-icon-wrapper">
                <div class="help-icon" :style="{ color: mode.color }">
                  <i :class="mode.icon"></i>
                </div>
                <div class="icon-decoration" :style="{ background: mode.color }"></div>
              </div>
              <div class="help-text">
                <div class="help-header-content">
                  <h4>{{ mode.label }}</h4>
                  <div class="mode-tag" :style="{ background: mode.color + '20', color: mode.color }">
                    {{ getModeTag(mode.value) }}
                  </div>
                </div>
                <div class="help-features">
                  <div class="feature-item" v-for="feature in getModeFeatures(mode.value)" :key="feature">
                    <i class="el-icon-check"></i>
                    <span>{{ feature }}</span>
                  </div>
                </div>
                <p class="help-desc">{{ getModeDescription(mode.value) }}</p>
                <div class="help-example">
                  <div class="example-tag">对话示例</div>
                  <div class="example-content">
                    <TypewriterText 
                      :text="getModeExample(mode.value)"
                      :key="mode.value"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <div class="animals-group">
      <!-- 猫咪 -->
      <div class="animal cat">
        <div class="cat-ears">
          <div class="ear-left"></div>
          <div class="ear-right"></div>
        </div>
        <div class="cat-face">
          <div class="eyes">
            <div class="eye left"></div>
            <div class="eye right"></div>
          </div>
          <div class="nose"></div>
          <div class="mouth"></div>
          <div class="whiskers">
            <div class="whisker-left"></div>
            <div class="whisker-right"></div>
          </div>
        </div>
        <div class="cat-body">
          <div class="paw left"></div>
          <div class="paw right"></div>
          <div class="tail"></div>
        </div>
      </div>

      <!-- 兔子 -->
      <div class="animal rabbit">
        <div class="rabbit-ears">
          <div class="ear-left">
            <div class="inner-ear"></div>
          </div>
          <div class="ear-right">
            <div class="inner-ear"></div>
          </div>
        </div>
        <div class="rabbit-face">
          <div class="eyes">
            <div class="eye left"></div>
            <div class="eye right"></div>
          </div>
          <div class="nose"></div>
          <div class="whiskers">
            <div class="whisker-left"></div>
            <div class="whisker-right"></div>
          </div>
        </div>
        <div class="rabbit-body">
          <div class="paw left"></div>
          <div class="paw right"></div>
          <div class="tail-ball"></div>
        </div>
      </div>

      <!-- 小熊 -->
      <div class="animal bear">
        <div class="bear-ears">
          <div class="ear-left">
            <div class="inner-ear"></div>
          </div>
          <div class="ear-right">
            <div class="inner-ear"></div>
          </div>
        </div>
        <div class="bear-face">
          <div class="eyes">
            <div class="eye left"></div>
            <div class="eye right"></div>
          </div>
          <div class="nose"></div>
          <div class="mouth"></div>
        </div>
        <div class="bear-body">
          <div class="paw left"></div>
          <div class="paw right"></div>
          <div class="belly"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, h } from 'vue'
import { defineComponent } from 'vue'

const showModePanel = ref(false)
const currentMode = ref('normal')
const showHelpPanel = ref(false)

const modes = [
  {
    value: 'casual',
    label: '轻松模式',
    icon: 'el-icon-coffee-cup',
    description: '用简单易懂的方式解释',
    color: '#67C23A'
  },
  {
    value: 'normal',
    label: '标准模式',
    icon: 'el-icon-light-rain',
    description: '平衡专业性和易懂性',
    color: '#409EFF'
  },
  {
    value: 'professional',
    label: '专业模式',
    icon: 'el-icon-trophy',
    description: '使用专业术语深入解析',
    color: '#E6A23C'
  },
  {
    value: 'expert',
    label: '专家模式',
    icon: 'el-icon-medal',
    description: '提供学术级别的详细分析',
    color: '#F56C6C'
  }
]

const toggleModePanel = () => {
  showModePanel.value = !showModePanel.value
}

const selectMode = (mode) => {
  currentMode.value = mode.value
  // 触发事件通知父组件模式已更改
  emit('update:mode', mode.value)
  showModePanel.value = false
}

const getModeDescription = (mode) => {
  const descriptions = {
    casual: '以轻松友好的语气回答，使用日常用语和简单的比喻，适合初学者和需要简单解释的场景。回答会更加生动有趣，避免使用专业术语。',
    normal: '平衡专业性和易懂性，使用清晰的解释并适当引入专业概念。这是默认的回答模式，适合大多数用户的日常使用。',
    professional: '使用更多专业术语和深入的技术细节，提供完整的解决方案和原理分析。适合有一定基础的用户和需要专业指导的场景。',
    expert: '提供最专业和深入的技术讨论，包含源码级别的分析、性能优化建议和最佳实践。适合专业开发者和需要深度技术探讨的场景。'
  }
  return descriptions[mode]
}

const getModeTag = (mode) => {
  const tags = {
    casual: '轻松对话',
    normal: '日常交流',
    professional: '专业解答',
    expert: '深度探讨'
  }
  return tags[mode]
}

const getModeFeatures = (mode) => {
  const features = {
    casual: [
      '生动有趣的比喻',
      '通俗易懂的解释',
      '友好轻松的语气'
    ],
    normal: [
      '清晰的概念讲解',
      '适度的专业术语',
      '实用的解决方案'
    ],
    professional: [
      '专业的技术分析',
      '完整的原理讲解',
      '深入的问题诊断'
    ],
    expert: [
      '源码级别分析',
      '性能优化建议',
      '架构设计指导'
    ]
  }
  return features[mode]
}

const getModeExample = (mode) => {
  const examples = {
    casual: '想象一下，函数就像一个会自动帮你完成任务的小助手...',
    normal: '这个函数的主要作用是处理用户输入并返回格式化后的数据...',
    professional: '该函数实现了异步数据处理，使用Promise处理并发请求...',
    expert: '从底层实现来看，这里采用了发布订阅模式优化性能...'
  }
  return examples[mode]
}

// 定义要向父组件发出的事件
const emit = defineEmits(['update:mode'])

const TypewriterText = defineComponent({
  props: {
    text: {
      type: String,
      required: true
    },
    speed: {
      type: Number,
      default: 50
    }
  },
  setup(props) {
    const displayText = ref('')
    let currentIndex = 0
    let timer = null

    const typeText = () => {
      if (currentIndex < props.text.length) {
        displayText.value += props.text[currentIndex]
        currentIndex++
        timer = setTimeout(typeText, props.speed)
      }
    }

    const resetAndStartTyping = () => {
      if (timer) clearTimeout(timer)
      displayText.value = ''
      currentIndex = 0
      setTimeout(typeText, 500) // 添加延迟，让动画更自然
    }

    onMounted(resetAndStartTyping)

    watch(() => props.text, resetAndStartTyping)

    onBeforeUnmount(() => {
      if (timer) clearTimeout(timer)
    })

    return () => h('div', { class: 'typewriter-text' }, [
      displayText.value,
      h('span', { class: 'cursor' }, '|')
    ])
  }
})

// 注册组件
const components = {
  TypewriterText
}
</script>

<style scoped>
.chat-animals {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  justify-content: space-between;
  padding: 0 40px;
}

.animals-group {
  display: flex;
  gap: 5px;
  align-items: flex-end;
  pointer-events: none;
}

.animal {
  position: relative;
  width: 45px;
  height: 60px;
  transform-origin: bottom center;
  animation: sway 3s ease-in-out infinite;
}

/* 通用身体样式 */
.paw {
  position: absolute;
  width: 12px;
  height: 8px;
  background: inherit;
  border-radius: 6px;
  bottom: 0;
}

.paw.left {
  left: 8px;
}

.paw.right {
  right: 8px;
}

/* 猫咪样式优化 */
.cat {
  animation-delay: 0s;
}

.cat-ears {
  position: absolute;
  top: -8px;
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.cat-ears .ear-left,
.cat-ears .ear-right {
  width: 12px;
  height: 15px;
  background: var(--el-color-primary);
  border-radius: 6px 6px 0 0;
  position: relative;
}

.cat-face {
  width: 35px;
  height: 35px;
  background: var(--el-color-primary-light-3);
  border-radius: 50%;
  position: relative;
  margin: auto;
}

.cat-body {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 25px;
  background: var(--el-color-primary-light-3);
  border-radius: 15px 15px 12px 12px;
}

.cat .tail {
  position: absolute;
  bottom: 15px;
  right: -5px;
  width: 12px;
  height: 20px;
  background: var(--el-color-primary-light-3);
  border-radius: 6px;
  transform-origin: bottom center;
  animation: tailWag 2s ease-in-out infinite;
}

/* 兔子样式优化 */
.rabbit {
  animation-delay: 0.2s;
}

.rabbit-ears {
  position: absolute;
  top: -15px;
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.rabbit-ears .ear-left,
.rabbit-ears .ear-right {
  width: 8px;
  height: 20px;
  background: var(--el-color-success-light-3);
  border-radius: 4px 4px 0 0;
}

.rabbit-face {
  width: 32px;
  height: 32px;
  background: var(--el-color-success-light-5);
  border-radius: 50%;
  position: relative;
  margin: auto;
}

.rabbit-body {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 22px;
  background: var(--el-color-success-light-5);
  border-radius: 14px 14px 10px 10px;
}

.rabbit .tail-ball {
  position: absolute;
  bottom: 5px;
  right: -3px;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}

.rabbit .inner-ear {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 14px;
  background: pink;
  border-radius: 2px;
  opacity: 0.6;
}

/* 小熊样式优化 */
.bear {
  animation-delay: 0.4s;
}

.bear-ears {
  position: absolute;
  top: -5px;
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.bear-ears .ear-left,
.bear-ears .ear-right {
  width: 10px;
  height: 10px;
  background: var(--el-color-warning);
  border-radius: 50%;
}

.bear-face {
  width: 38px;
  height: 38px;
  background: var(--el-color-warning-light-3);
  border-radius: 50%;
  position: relative;
  margin: auto;
}

.bear-body {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 34px;
  height: 28px;
  background: var(--el-color-warning-light-3);
  border-radius: 17px 17px 14px 14px;
}

.bear .belly {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
}

.bear .inner-ear {
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: var(--el-color-warning-dark-2);
  border-radius: 50%;
  opacity: 0.6;
}

/* 胡须样式 */
.whiskers {
  position: absolute;
  bottom: 35%;
  left: 0;
  right: 0;
  height: 8px;
}

.whisker-left, .whisker-right {
  position: absolute;
  width: 12px;
  height: 1px;
  background: rgba(0, 0, 0, 0.2);
}

.whisker-left {
  left: -8px;
  transform: rotate(-10deg);
}

.whisker-left::before,
.whisker-left::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 1px;
  background: inherit;
  transform-origin: right;
}

.whisker-left::before {
  top: -3px;
  transform: rotate(-15deg);
}

.whisker-left::after {
  bottom: -3px;
  transform: rotate(15deg);
}

.whisker-right {
  right: -8px;
  transform: rotate(10deg);
}

.whisker-right::before,
.whisker-right::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 1px;
  background: inherit;
  transform-origin: left;
}

.whisker-right::before {
  top: -3px;
  transform: rotate(15deg);
}

.whisker-right::after {
  bottom: -3px;
  transform: rotate(-15deg);
}

/* 动画优化 */
@keyframes sway {
  0%, 100% {
    transform: rotate(-2deg);
  }
  50% {
    transform: rotate(2deg);
  }
}

@keyframes tailWag {
  0%, 100% {
    transform: rotate(-5deg);
  }
  50% {
    transform: rotate(5deg);
  }
}

/* 通用眼睛和鼻子样式 */
.eyes {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  display: flex;
  justify-content: space-between;
}

.eye {
  width: 4px;
  height: 4px;
  background: #333;
  border-radius: 50%;
}

.nose {
  position: absolute;
  bottom: 30%;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #333;
  border-radius: 50%;
}

.mouth {
  position: absolute;
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 3px;
  border-bottom: 2px solid #333;
  border-radius: 50%;
}

/* 眨眼动画 */
.eye {
  animation: blink 4s infinite;
}

@keyframes blink {
  0%, 96%, 98% {
    transform: scaleY(1);
  }
  97% {
    transform: scaleY(0.1);
  }
}

/* 小狗样式 */
.dog {
  position: relative;
  width: 80px;
  height: 45px;
  transform: rotate(5deg);
  animation: breathe 4s ease-in-out infinite;
}

.dog-ears {
  position: absolute;
  top: -5px;
  left: 5px;
  width: 30px;
  display: flex;
  justify-content: space-between;
  z-index: 1;
}

.dog-ears .ear-left,
.dog-ears .ear-right {
  width: 12px;
  height: 15px;
  background: var(--el-color-info);
  border-radius: 6px;
  transform-origin: bottom center;
}

.dog-ears .ear-left {
  transform: rotate(-30deg);
}

.dog-ears .ear-right {
  transform: rotate(30deg);
}

.dog-face {
  position: absolute;
  top: 0;
  left: 0;
  width: 35px;
  height: 35px;
  background: var(--el-color-info-light-3);
  border-radius: 50%;
  z-index: 2;
}

.dog-body {
  position: absolute;
  top: 15px;
  left: 20px;
  width: 60px;
  height: 30px;
  background: var(--el-color-info-light-3);
  border-radius: 15px;
  transform: rotate(-5deg);
}

.dog .belly {
  position: absolute;
  bottom: 2px;
  left: 5px;
  width: 50px;
  height: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 25px / 10px;
}

.dog .legs {
  position: absolute;
  bottom: -5px;
  left: 10px;
  width: 40px;
  display: flex;
  justify-content: space-between;
}

.dog .leg {
  width: 12px;
  height: 8px;
  background: var(--el-color-info-light-3);
  border-radius: 6px;
}

.dog .tail {
  position: absolute;
  top: 5px;
  right: -8px;
  width: 15px;
  height: 8px;
  background: var(--el-color-info-light-3);
  border-radius: 4px;
  transform-origin: left center;
  animation: wagTail 2s ease-in-out infinite;
}

.dog .nose {
  background: #333;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  bottom: 40%;
  left: 25%;
}

.dog .mouth {
  position: absolute;
  bottom: 30%;
  left: 25%;
  width: 12px;
  height: 6px;
  border-bottom: 2px solid #333;
  border-radius: 50%;
}

@keyframes breathe {
  0%, 100% {
    transform: rotate(5deg) scale(1);
  }
  50% {
    transform: rotate(5deg) scale(1.02);
  }
}

@keyframes wagTail {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(20deg);
  }
}

/* 使小狗可点击 */
.dog.clickable {
  pointer-events: auto !important;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.dog.clickable:hover {
  transform: rotate(5deg) scale(1.05);
}

.dog.active {
  transform: rotate(5deg) scale(1.1);
}

/* 模式选择面板样式 */
.mode-panel {
  position: absolute;
  left: 20px;
  bottom: 70px;
  width: 280px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
  pointer-events: auto;
}

.panel-header {
  padding: 14px 18px;
  background: linear-gradient(to right, var(--el-color-primary-light-8), var(--el-color-primary-light-9));
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--el-color-primary);
  font-weight: 600;
  pointer-events: auto;
}

.close-icon {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s;
  pointer-events: auto;
}

.close-icon:hover {
  background-color: var(--el-color-primary-light-9);
}

.mode-options {
  padding: 8px;
  pointer-events: auto;
}

.mode-option {
  display: flex;
  align-items: center;
  padding: 14px;
  margin: 6px 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.mode-option:hover {
  background: var(--el-color-primary-light-9);
  transform: translateX(4px);
}

.mode-option:hover .mode-icon {
  transform: scale(1.1) rotate(5deg);
}

.mode-option:hover .mode-icon i {
  transform: scale(1.1);
}

.mode-option.active {
  background: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-5);
}

.mode-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.mode-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: currentColor;
  opacity: 0.1;
}

.mode-icon::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0) 100%);
}

.mode-icon i {
  font-size: 24px;
  color: currentColor;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.mode-info {
  flex: 1;
  pointer-events: auto;
}

.mode-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--el-text-color-primary);
  font-size: 15px;
  transition: all 0.3s ease;
}

.mode-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
  transition: all 0.3s ease;
}

.mode-option:hover .mode-title {
  color: var(--el-color-primary);
}

.mode-option:hover .mode-desc {
  color: var(--el-text-color-regular);
}

/* 为每个模式设置不同的颜色 */
.mode-option:nth-child(1) .mode-icon {
  color: #67C23A;
}

.mode-option:nth-child(2) .mode-icon {
  color: #409EFF;
}

.mode-option:nth-child(3) .mode-icon {
  color: #E6A23C;
}

.mode-option:nth-child(4) .mode-icon {
  color: #F56C6C;
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* 确保小狗在面板之下 */
.dog {
  z-index: 99;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.help-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-color-primary);
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.help-btn:hover {
  background: var(--el-color-primary-light-8);
}

.help-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.help-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  max-width: 90vw;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.help-header {
  padding: 16px 20px;
  background: linear-gradient(to right, var(--el-color-primary-light-7), var(--el-color-primary-light-8));
  color: var(--el-color-primary-dark-2);
  font-weight: 600;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-content {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.help-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  transition: all 0.3s;
  margin-bottom: 12px;
  border: 1px solid var(--el-border-color-light);
}

.help-item:hover {
  background: var(--el-color-primary-light-9);
  transform: translateX(4px);
}

.help-icon-wrapper {
  position: relative;
  margin-right: 16px;
}

.icon-decoration {
  position: absolute;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  opacity: 0.1;
  transform: rotate(10deg);
  transition: all 0.3s ease;
}

.help-item:hover .icon-decoration {
  transform: rotate(-5deg) scale(1.2);
}

.help-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.mode-tag {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.help-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--el-color-primary-light-9);
  border-radius: 4px;
  font-size: 12px;
}

.feature-item i {
  font-size: 12px;
  color: var(--el-color-success);
}

.help-example {
  margin-top: 12px;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  overflow: hidden;
}

.example-tag {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
}

.example-content {
  padding: 12px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  font-style: italic;
}

.help-icon {
  z-index: 1;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.help-text h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.help-desc {
  margin: 12px 0;
  color: var(--el-text-color-secondary);
}

.close-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: normal;
  color: var(--el-color-primary-dark-2);
}

.close-tip .close-icon {
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-tip .close-icon:hover {
  background: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
}

.typewriter-text {
  display: inline-block;
  white-space: pre-wrap;
  word-break: break-word;
}

.cursor {
  display: inline-block;
  width: 2px;
  animation: blink 0.7s infinite;
  color: var(--el-color-primary);
  font-weight: bold;
  margin-left: 2px;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.example-content {
  min-height: 48px;
  display: flex;
  align-items: center;
}
</style> 