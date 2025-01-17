import { ref } from 'vue'
import { useRouter } from 'vue-router'

export function useLogin() {
  const router = useRouter()
  const formData = ref({
    username: '',
    password: '',
    rememberMe: false,
    autoLogin: false
  })

  const isLoading = ref(false)
  const error = ref('')

  const handleLogin = async () => {
    try {
      isLoading.value = true
      error.value = ''
      
      // TODO: 实现登录逻辑
      console.log('Login attempt:', formData.value)
      
      // 模拟登录延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // TODO: 处理登录成功后的逻辑
      // router.push('/dashboard')
    } catch (err) {
      error.value = err.message || '登录失败，请重试'
    } finally {
      isLoading.value = false
    }
  }

  return {
    formData,
    isLoading,
    error,
    handleLogin
  }
} 