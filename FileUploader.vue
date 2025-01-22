<template>
  <div class="file-uploader">
    <input
      type="file"
      ref="fileInput"
      @change="handleFileSelect"
      accept=".txt"
      multiple
      class="file-input"
    />
    <el-button 
      type="primary"
      :plain="true"
      @click="triggerFileInput"
      class="upload-button"
    >
      <template #icon>
        <el-icon><Upload /></el-icon>
      </template>
      上传文件
    </el-button>

    <!-- 上传列表 -->
    <div class="upload-list" v-if="uploadedFiles.length > 0">
      <div class="file-item" v-for="file in uploadedFiles" :key="file.name">
        <span class="file-name">{{ file.name }}</span>
        <span class="file-status" :class="file.status">{{ file.statusText }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { Upload } from '@element-plus/icons-vue'
import axios from 'axios';

export default {
  name: 'FileUploader',
  components: {
    Upload
  },
  data() {
    return {
      uploadedFiles: []
    };
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleDrop(e) {
      const files = [...e.dataTransfer.files];
      this.uploadFiles(files);
    },
    handleFileSelect(e) {
      const files = [...e.target.files];
      this.uploadFiles(files);
    },
    async uploadFiles(files) {
      for (const file of files) {
        if (!file.name.endsWith('.txt')) {
          this.$message.error('只支持上传 .txt 文件');
          continue;
        }

        const fileInfo = {
          name: file.name,
          status: 'uploading',
          statusText: '上传中...'
        };
        this.uploadedFiles.push(fileInfo);

        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await axios.post('http://localhost:5000/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
            timeout: 30000, // 30 seconds timeout
            validateStatus: function (status) {
              return status >= 200 && status < 300;
            }
          });

          if (response.data.message) {
            fileInfo.status = 'success';
            fileInfo.statusText = '上传成功';
            this.$message.success(`${file.name} 上传成功`);
          } else {
            throw new Error(response.data.error || '上传失败');
          }
        } catch (error) {
          console.error('Upload error:', error);
          fileInfo.status = 'error';
          fileInfo.statusText = `上传失败: ${error.message}`;
          this.$message.error(`${file.name} 上传失败: ${error.message}`);
          
          // 如果是网络错误，尝试重试
          if (error.message.includes('network') || error.message.includes('timeout')) {
            try {
              fileInfo.statusText = '正在重试...';
              await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
              const retryResponse = await axios.post('http://localhost:5000/upload', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                },
                maxContentLength: Infinity,
                maxBodyLength: Infinity,
                timeout: 30000
              });
              
              if (retryResponse.data.message) {
                fileInfo.status = 'success';
                fileInfo.statusText = '上传成功（重试）';
                this.$message.success(`${file.name} 重试上传成功`);
              }
            } catch (retryError) {
              console.error('Retry upload error:', retryError);
              fileInfo.status = 'error';
              fileInfo.statusText = `重试上传失败: ${retryError.message}`;
              this.$message.error(`${file.name} 重试上传失败: ${retryError.message}`);
            }
          }
        }
      }
    }
  }
};
</script>

<style scoped>
.file-uploader {
  display: inline-block;
}

.file-input {
  display: none;
}

.upload-button {
  font-size: 14px;
}

.upload-list {
  margin-top: 10px;
  font-size: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.file-name {
  color: var(--el-text-color-regular);
}

.file-status {
  font-size: 12px;
}

.file-status.uploading {
  color: var(--el-color-primary);
}

.file-status.success {
  color: var(--el-color-success);
}

.file-status.error {
  color: var(--el-color-danger);
}
</style>
