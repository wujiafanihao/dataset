<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="typing-title">WUJIAFA</h1>
      <p class="login-subtitle">数据标注系统</p>
      
      <form @submit.prevent="handleLogin" autocomplete="off">
        <div class="input-group">
          <input
            id="username"
            v-model="formData.username"
            type="text"
            required
            class="input-field"
            placeholder="输入用户名"
            :disabled="isLoading"
          />
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            class="input-field"
            placeholder="输入密码"
            :disabled="isLoading"
          />
        </div>

        <div class="checkbox-group">
          <div class="checkbox-container">
            <input
              id="remember-me"
              v-model="formData.rememberMe"
              type="checkbox"
              class="checkbox-input"
              :disabled="isLoading"
            />
            <label for="remember-me" class="checkbox-label">记住密码</label>
          </div>

          <div class="checkbox-container">
            <input
              id="auto-login"
              v-model="formData.autoLogin"
              type="checkbox"
              class="checkbox-input"
              :disabled="isLoading"
            />
            <label for="auto-login" class="checkbox-label">自动登录</label>
          </div>
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="isLoading"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>

        <transition name="fade">
          <p v-if="error" class="error-message">{{ error }}</p>
        </transition>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useLogin } from '../composables/useLogin'
import '../styles/login.css'

const { formData, isLoading, error, handleLogin } = useLogin()
</script> 