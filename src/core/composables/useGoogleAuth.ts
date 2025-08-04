/**
 * Google 인증 상태 관리를 위한 컴포저블
 */
import { ref, computed, onMounted } from 'vue'
import { useToast } from './useToast'

interface GoogleAuthStatus {
  authenticated: boolean
  services_available: boolean
  error?: string
}

interface GoogleAuthData {
  auth_url: string
}

export function useGoogleAuth() {
  const toast = useToast()
  
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const servicesAvailable = ref(false)
  const error = ref<string | null>(null)
  const lastChecked = ref<Date | null>(null)
  
  const authStatus = computed(() => {
    if (isLoading.value) return 'loading'
    if (error.value) return 'error'
    if (isAuthenticated.value) return 'authenticated'
    return 'not_authenticated'
  })
  
  const statusColor = computed(() => {
    switch (authStatus.value) {
      case 'authenticated': return 'text-green-600 dark:text-green-400'
      case 'error': return 'text-red-600 dark:text-red-400'
      case 'loading': return 'text-yellow-600 dark:text-yellow-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  })
  
  const statusText = computed(() => {
    switch (authStatus.value) {
      case 'authenticated': return 'Google 계정 연결됨'
      case 'error': return error.value || 'Google 서비스 오류'
      case 'loading': return '상태 확인 중...'
      default: return 'Google 계정 연결 필요'
    }
  })
  
  const statusIcon = computed(() => {
    switch (authStatus.value) {
      case 'authenticated': return '✅'
      case 'error': return '❌'
      case 'loading': return '🔄'
      default: return '🔗'
    }
  })
  
  /**
   * Google 인증 상태 확인
   */
  const checkAuthStatus = async (): Promise<void> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/google/status')
      const data: GoogleAuthStatus = await response.json()
      
      if (response.ok) {
        isAuthenticated.value = data.authenticated
        servicesAvailable.value = data.services_available
        
        if (data.error) {
          error.value = data.error
        }
        
        lastChecked.value = new Date()
      } else {
        throw new Error('Google 서비스 상태 확인 실패')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Google 서비스 연결 실패'
      servicesAvailable.value = false
      isAuthenticated.value = false
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Google 인증 시작
   */
  const startAuth = async (): Promise<void> => {
    if (!servicesAvailable.value) {
      toast.error('Google 서비스 사용 불가', {
        description: 'Google 서비스를 사용할 수 없습니다.'
      })
      return
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/google/auth')
      const data: GoogleAuthData = await response.json()
      
      if (response.ok && data.auth_url) {
        // 새 창에서 Google 인증 페이지 열기
        const authWindow = window.open(
          data.auth_url,
          'google_auth',
          'width=500,height=600,scrollbars=yes,resizable=yes'
        )
        
        // 인증 완료 감지를 위한 메시지 리스너
        const handleMessage = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return
          
          if (event.data === 'google_auth_success') {
            authWindow?.close()
            window.removeEventListener('message', handleMessage)
            
            toast.success('🎉 Google 연동 성공!', {
              description: 'Google 서비스 연동이 완료되었습니다! 이제 @캘린더, @메일 기능을 사용할 수 있습니다.',
              duration: 5000
            })
            
            console.log('✅ Google OAuth 팝업에서 성공 신호를 받았습니다.')
            
            // 상태 다시 확인
            setTimeout(() => {
              checkAuthStatus()
            }, 1000)
          } else if (event.data === 'google_auth_error') {
            authWindow?.close()
            window.removeEventListener('message', handleMessage)
            
            toast.error('❌ Google 연동 실패', {
              description: 'Google 서비스 연동에 실패했습니다. 다시 시도해주세요.',
              duration: 5000
            })
            
            console.log('❌ Google OAuth 팝업에서 실패 신호를 받았습니다.')
          }
        }
        
        window.addEventListener('message', handleMessage)
        
        // 창이 닫힌 경우 처리
        const checkClosed = setInterval(() => {
          if (authWindow?.closed) {
            clearInterval(checkClosed)
            window.removeEventListener('message', handleMessage)
            isLoading.value = false
          }
        }, 1000)
        
      } else {
        throw new Error('인증 URL을 가져올 수 없습니다.')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Google 인증 시작 실패'
      toast.error('Google 인증 오류', {
        description: error.value
      })
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Google 계정 연결 해제
   */
  const disconnect = async (): Promise<void> => {
    try {
      // 토큰 파일 삭제를 위한 API 호출 (필요시 백엔드에 구현)
      // await fetch('http://localhost:8000/api/v1/google/disconnect', { method: 'POST' })
      
      isAuthenticated.value = false
      lastChecked.value = null
      
      toast.success('Google 계정 연결 해제', {
        description: '계정 연결이 해제되었습니다.'
      })
    } catch (err) {
      toast.error('연결 해제 실패', {
        description: '계정 연결 해제 중 오류가 발생했습니다.'
      })
    }
  }
  
  /**
   * URL 매개변수에서 인증 결과 확인
   */
  const checkUrlParams = (): void => {
    const urlParams = new URLSearchParams(window.location.search)
    const googleAuth = urlParams.get('google_auth')
    const message = urlParams.get('message') // 백엔드에서 전달된 메시지
    
    if (googleAuth === 'success') {
      // 부모 창에 성공 메시지 전송
      if (window.opener) {
        window.opener.postMessage('google_auth_success', window.location.origin)
        window.close()
      } else {
        toast.success('🎉 Google 연동 성공!', {
          description: message || 'Google 서비스 연동이 성공적으로 완료되었습니다! 이제 캘린더와 이메일을 사용할 수 있습니다.',
          duration: 5000 // 5초간 표시
        })
        console.log('✅ Google OAuth 성공: 인증 상태를 다시 확인합니다.')
        checkAuthStatus()
      }
      
      // URL에서 매개변수 제거
      window.history.replaceState({}, document.title, window.location.pathname)
    } else if (googleAuth === 'error') {
      // 부모 창에 오류 메시지 전송
      if (window.opener) {
        window.opener.postMessage('google_auth_error', window.location.origin)
        window.close()
      } else {
        toast.error('❌ Google 연동 실패', {
          description: message || 'Google 서비스 연동에 실패했습니다. 다시 시도해주세요.',
          duration: 5000 // 5초간 표시
        })
        console.log('❌ Google OAuth 실패: 연동에 실패했습니다.')
      }
      
      // URL에서 매개변수 제거
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }
  
  // 컴포넌트 마운트 시 상태 확인
  onMounted(() => {
    checkUrlParams()
    checkAuthStatus()
  })
  
  return {
    // 상태
    isAuthenticated,
    isLoading,
    servicesAvailable,
    error,
    lastChecked,
    authStatus,
    statusColor,
    statusText,
    statusIcon,
    
    // 메서드
    checkAuthStatus,
    startAuth,
    disconnect,
    checkUrlParams
  }
}