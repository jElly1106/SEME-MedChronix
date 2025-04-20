<template>
  <div class="chat-container">
    <h3>AI咨询</h3>
    <!-- 显示消息 -->
    <div class="messages">
      <div
        v-for="message in chatMessages"
        :class="['message', message.sender]"
        :key="message.id"
      >
        <div class="message-content">
          <span v-if="message.type === 'image'">
            <img
              :src="message.content"
              alt="User uploaded image"
              class="uploaded-image"
            />
          </span>
          <div v-else v-html="parseMarkdown(message.content)"></div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-container">
      <div v-if="uploadedImage" class="uploaded-preview">
        <img :src="uploadedImage" alt="Uploaded Image" class="image-preview" />
        <button class="close-preview-btn" @click="removeImage">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="input-row">
        <button class="upload-btn" @click="triggerFileInput">
          <i class="fas fa-plus"></i>
        </button>
        <input type="file" ref="fileInput" @change="handleFileChange" />
        <textarea
          v-model="userInput"
          placeholder="输入问题..."
          rows="3"
        ></textarea>
        <button @click="sendMessage" class="submit-btn">
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from "marked";

export default {
  name: "ChatBox",
  data() {
    return {
      userInput: "",
      selectedFile: null,
      uploadedImage: null,
      chatMessages: [],
    };
  },
  methods: {
    parseMarkdown(text) {
      return marked(text || "");
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadedImage = URL.createObjectURL(file);
        this.selectedFile = file;
      }
    },
    removeImage() {
      this.uploadedImage = null;
      this.$refs.fileInput.value = "";
      this.selectedFile = null;
    },
    sendMessage() {
      if (this.userInput.trim()) {
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: this.userInput,
          sender: "user",
          type: "text",
        });
      }

      if (this.selectedFile) {
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: "正在分析图片，请稍候...",
          sender: "bot",
          type: "text",
        });

        const formData = new FormData();
        formData.append("image", this.selectedFile);

        fetch("http://127.0.0.1:5000/api/llm/image-analysis", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "正在分析图片，请稍候..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: data.result,
              sender: "bot",
              type: "text",
            });
          })
          .catch((error) => {
            console.error("图片分析错误:", error);
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "正在分析图片，请稍候..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: "抱歉，图片分析失败。",
              sender: "bot",
              type: "text",
            });
          });

        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: this.uploadedImage,
          sender: "user",
          type: "image",
        });

        this.uploadedImage = null;
        this.selectedFile = null;
      } else if (this.userInput.trim()) {
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: "回答的内容将自动生成...",
          sender: "bot",
          type: "text",
        });

        fetch("http://127.0.0.1:5000/api/llm/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: this.userInput }),
        })
          .then((response) => response.json())
          .then((data) => {
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "回答的内容将自动生成..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: data.response,
              sender: "bot",
              type: "text",
            });
          })
          .catch((error) => {
            console.error("聊天接口错误:", error);
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "回答的内容将自动生成..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: "抱歉，我无法回答您的问题。",
              sender: "bot",
              type: "text",
            });
          });
      }

      this.userInput = "";
    },
  },
};
</script>

<style scoped>
.chat-container {
  background-color: #f7f7f7;
  border-radius: 8px;
  padding-left: 10px;
  padding-bottom: 15px; /* 增加底部内边距，为输入框留出空间 */
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  overflow: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: relative; /* 为内部绝对定位元素提供参照 */
}

/* 消息区域调整，确保留出足够空间给输入框 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  padding-bottom: 60px; /* 增加底部内边距，为固定定位的输入框留出空间 */
}

/* 每条消息的样式 */
.message {
  margin-bottom: 10px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

/* 医生消息和大模型消息的样式 */
.message.user {
  justify-content: flex-end; /* 医生消息靠右 */
}

.message.bot {
  justify-content: flex-start; /* 大模型消息靠左 */
}

.message .message-content {
  max-width: 80%;
  padding: 0px 10px;
  border-radius: 10px;
  font-size: 14px;
}

.message.user .message-content {
  background-color: #c6d2fd;
  color: black;
}

.message.bot .message-content {
  background-color: #e5eafc;
  color: black;
  text-align: left;
}
.uploaded-image {
  max-width: 100%;
  border-radius: 5px;
}

/* 输入框固定底部 */
/* 外层容器 - 垂直布局，图片预览在上，输入行在下 */
.input-container {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  background-color: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 30px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 10px 15px;
  position: absolute; /* 改为绝对定位，避免在flex布局中被压缩 */
  bottom: 10px; /* 距离底部10px */
  left: 50%; /* 水平居中 */
  transform: translateX(-50%); /* 水平居中 */
  width: 90%; /* 宽度占90% */
  z-index: 10;
  min-height: 56px; /* 设置最小高度确保不会被压得太扁 */
}

/* 输入行样式调整 */
.input-row {
  display: flex;
  align-items: center;
  min-height: 36px; /* 确保最小高度 */
}

/* 文本输入框调整 */
.input-row textarea {
  flex: 1;
  min-height: 36px;
  border: none;
  outline: none;
  resize: none;
  background-color: transparent;
  font-size: 16px;
  color: #333;
  padding: 5px 0; /* 增加上下内边距 */
  margin-right: 10px;
  line-height: 1.4; /* 改善多行文本的行间距 */
}

/* 上传预览区域调整 */
.uploaded-preview {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 8px; /* 与输入行保持间距 */
}

.image-preview {
  position: relative;
  display: block;
  width: 40px; /* 稍微加大图片预览 */
  height: 40px;
  border-radius: 5px;
  object-fit: cover;
  margin-right: 5px;
}

/* 关闭按钮 - 右上角 */
.close-preview-btn {
  position: relative;
  top: -20px;
  right: 10px; /* 改为右上角位置，更符合常规设计 */
  width: 20px; /* 增加尺寸 */
  height: 20px; /* 增加尺寸 */
  background-color: #ff4757; /* 更醒目的红色 */
  color: #fff;
  border: 2px solid #fff; /* 添加白色边框增强立体感 */
  border-radius: 50%;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); /* 增强阴影 */
  z-index: 11; /* 确保在最上层 */
  transition: all 0.2s ease; /* 平滑过渡效果 */
  padding: 0; /* 重置内边距 */
  line-height: 1; /* 确保内容垂直居中 */
}

/* 悬停时变亮一些 */
.close-preview-btn:hover {
  background-color: #999;
}

/* 输入行（+号按钮、文本域、发送按钮）并排 */
.input-row {
  display: flex;
  align-items: center;
}

/* “+”号上传按钮 - 圆形 */
.upload-btn {
  width: 36px;
  height: 36px;
  background-color: #93aafd;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  margin-right: 10px; /* 与文本域拉开距离 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

/* 隐藏的文件选择框 */
.input-container input[type="file"] {
  display: none;
}

/* 文本输入框 - 占据剩余空间，简洁无边框 */
.input-row textarea {
  flex: 1; /* 撑满剩余宽度 */
  min-height: 36px; /* 保证与按钮等高 */
  border: none;
  outline: none;
  resize: none; /* 禁止拖拽缩放 */
  background-color: transparent;
  font-size: 16px;
  color: #333;
  padding: 0;
  margin-right: 10px; /* 与发送按钮拉开距离 */
}

/* 占位文字颜色 */
.input-row textarea::placeholder {
  color: #aaa;
}

/* 发送按钮（右箭头图标） - 圆形 */
.submit-btn {
  width: 36px;
  height: 36px;
  background-color: #2d5bff;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

/* 悬停时颜色变浅 */
.submit-btn:hover {
  background-color: #93aafd;
}
</style>
