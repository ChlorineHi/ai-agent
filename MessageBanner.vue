<template>
  <div class="message-banner">
    <div class="banner-content">
      <div class="model-selector">
        <el-dropdown 
          trigger="click" 
          @command="handleModelSelect"
          @visible-change="handleDropdownVisibleChange">
          <div class="model-button" :class="{ 'is-active': isDropdownVisible }">
            <component :is="getModelIcon(currentModel)" class="model-icon" />
            <span class="model-name">{{ currentModel }}</span>
            <el-icon class="arrow-icon" :class="{ 'is-reverse': isDropdownVisible }">
              <ArrowDown />
            </el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="model in models" 
                :key="model.value" 
                :command="model.value"
                :class="{ 'is-active': currentModel === model.label }">
                <component :is="getModelIcon(model.label)" class="item-icon" />
                <span class="item-label">{{ model.label }}</span>
                <el-icon v-if="currentModel === model.label" class="check-icon">
                  <Check />
                </el-icon>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ArrowDown, Check } from '@element-plus/icons-vue'
import { 
  Lightning, 
  MagicStick, 
  Cpu 
} from '@element-plus/icons-vue'

export default {
  name: 'MessageBanner',
  components: {
    ArrowDown,
    Check,
    Lightning,
    MagicStick,
    Cpu
  },
  setup(props, { emit }) {
    const currentModel = ref('GLM-4')
    const isDropdownVisible = ref(false)
    const models = [
      { label: 'GLM-4', value: 'zhipu' },
      { label: 'Deepseek', value: 'deepseek' }
    ]

    const getModelIcon = (modelName) => {
      const iconMap = {
        'GLM-4': Cpu,
        'Deepseek': MagicStick
      }
      return iconMap[modelName] || Cpu
    }

    const handleModelSelect = (value) => {
      const selectedModel = models.find(m => m.value === value)
      if (selectedModel) {
        currentModel.value = selectedModel.label
        emit('model-change', value)
      }
    }

    const handleDropdownVisibleChange = (visible) => {
      isDropdownVisible.value = visible
    }

    return {
      currentModel,
      models,
      isDropdownVisible,
      handleModelSelect,
      handleDropdownVisibleChange,
      getModelIcon,
      ArrowDown,
      Check
    }
  }
}
</script>

<style scoped>
.message-banner {
  width: 100%;
  height: 1.2cm;
  background: white;
  padding: 8px 24px;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.message-banner:hover {
  background: #f9f9f9;
}

.banner-content {
  height: 100%;
  display: flex;
  align-items: center;
}

.model-selector {
  margin-right: 20px;
  position: relative;
}

.model-button {
  display: flex;
  align-items: center;
  height: 42px;
  padding: 0 18px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  gap: 12px;
}

.model-button:hover, .model-button.is-active {
  background: rgba(var(--el-color-primary-rgb), 0.1);
  color: var(--el-color-primary);
}

.model-icon {
  font-size: 22px;
  color: #409EFF;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  letter-spacing: 0.3px;
  background: linear-gradient(90deg, #222 30%, #555);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.model-button:hover .model-name,
.model-button.is-active .model-name {
  background: linear-gradient(90deg, var(--el-color-primary) 30%, var(--el-color-primary-light-3));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transform: scale(1.02);
}

.arrow-icon {
  font-size: 14px;
  color: #909399;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.arrow-icon.is-reverse {
  transform: rotate(180deg);
}

.model-button:hover .arrow-icon,
.model-button.is-active .arrow-icon {
  color: var(--el-color-primary);
}

:deep(.el-dropdown-menu) {
  padding: 8px;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  border: none;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(8px);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 3px;
  height: 48px;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
  color: var(--el-color-primary);
  transform: translateY(-1px);
}

:deep(.el-dropdown-menu__item.is-active) {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
  color: var(--el-color-primary);
}

.item-icon {
  font-size: 22px;
  margin-right: 12px;
  color: #409EFF;
}

.item-label {
  flex: 1;
  font-size: 16px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.check-icon {
  font-size: 16px;
  color: var(--el-color-primary);
  margin-left: 8px;
}
</style>
