import { ref, computed, watch } from 'vue'

export type ThemeName = 'default' | 'warm' | 'neutral'

export interface ThemeColors {
  light: Record<string, string>
  dark: Record<string, string>
}

// 기본 테마 (현재 오렌지 계열)
const defaultTheme: ThemeColors = {
  light: {
    '--background': 'oklch(0.98 0.005 85)',
    '--foreground': 'oklch(0.15 0.012 25)',
    '--card': 'oklch(0.985 0.008 85)',
    '--card-foreground': 'oklch(0.15 0.012 25)',
    '--popover': 'oklch(0.99 0.006 85)',
    '--popover-foreground': 'oklch(0.15 0.012 25)',
    '--primary': 'oklch(0.65 0.16 50)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.94 0.025 85)',
    '--secondary-foreground': 'oklch(0.15 0.025 25)',
    '--muted': 'oklch(0.95 0.02 85)',
    '--muted-foreground': 'oklch(0.35 0.02 25)',
    '--accent': 'oklch(0.92 0.03 85)',
    '--accent-foreground': 'oklch(0.1 0.02 25)',
    '--destructive': 'oklch(0.65 0.25 15)',
    '--destructive-foreground': 'oklch(0.98 0.005 85)',
    '--border': 'oklch(0.85 0.035 85)',
    '--input': 'oklch(0.97 0.015 85)',
    '--ring': 'oklch(0.65 0.16 50)',
    '--sidebar': 'oklch(0.985 0.008 85)',
    '--sidebar-foreground': 'oklch(0.15 0.012 25)',
    '--sidebar-primary': 'oklch(0.65 0.16 50)',
    '--sidebar-primary-foreground': 'oklch(1.0000 0 0)',
    '--sidebar-accent': 'oklch(0.92 0.03 85)',
    '--sidebar-accent-foreground': 'oklch(0.1 0.02 25)',
    '--sidebar-border': 'oklch(0.88 0.025 85)',
    '--sidebar-ring': 'oklch(0.65 0.16 50)',
  },
  dark: {
    '--background': 'oklch(0.2598 0.0306 262.6666)',
    '--foreground': 'oklch(0.9219 0 0)',
    '--card': 'oklch(0.3106 0.0301 268.6365)',
    '--card-foreground': 'oklch(0.9219 0 0)',
    '--popover': 'oklch(0.2900 0.0249 268.3986)',
    '--popover-foreground': 'oklch(0.9219 0 0)',
    '--primary': 'oklch(0.65 0.16 50)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.3095 0.0266 266.7132)',
    '--secondary-foreground': 'oklch(0.9219 0 0)',
    '--muted': 'oklch(0.35 0.035 266.7132)',
    '--muted-foreground': 'oklch(0.75 0.02 266.7132)',
    '--accent': 'oklch(0.3380 0.0589 267.5867)',
    '--accent-foreground': 'oklch(0.8823 0.0571 254.1284)',
    '--destructive': 'oklch(0.6368 0.2078 25.3313)',
    '--destructive-foreground': 'oklch(1.0000 0 0)',
    '--border': 'oklch(0.45 0.045 269.7337)',
    '--input': 'oklch(0.35 0.035 269.7337)',
    '--ring': 'oklch(0.65 0.16 50)',
    '--sidebar': 'oklch(0.3100 0.0283 267.7408)',
    '--sidebar-foreground': 'oklch(0.9219 0 0)',
    '--sidebar-primary': 'oklch(0.65 0.16 50)',
    '--sidebar-primary-foreground': 'oklch(1.0000 0 0)',
    '--sidebar-accent': 'oklch(0.3380 0.0589 267.5867)',
    '--sidebar-accent-foreground': 'oklch(0.8823 0.0571 254.1284)',
    '--sidebar-border': 'oklch(0.3843 0.0301 269.7337)',
    '--sidebar-ring': 'oklch(0.65 0.16 50)',
  },
}

// 새로운 따뜻한 테마
const warmTheme: ThemeColors = {
  light: {
    '--background': 'oklch(0.9818 0.0054 95.0986)',
    '--foreground': 'oklch(0.3438 0.0269 95.7226)',
    '--card': 'oklch(0.9818 0.0054 95.0986)',
    '--card-foreground': 'oklch(0.1908 0.0020 106.5859)',
    '--popover': 'oklch(1.0000 0 0)',
    '--popover-foreground': 'oklch(0.2671 0.0196 98.9390)',
    '--primary': 'oklch(0.6171 0.1375 39.0427)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.9245 0.0138 92.9892)',
    '--secondary-foreground': 'oklch(0.4334 0.0177 98.6048)',
    '--muted': 'oklch(0.9341 0.0153 90.2390)',
    '--muted-foreground': 'oklch(0.6059 0.0075 97.4233)',
    '--accent': 'oklch(0.9245 0.0138 92.9892)',
    '--accent-foreground': 'oklch(0.2671 0.0196 98.9390)',
    '--destructive': 'oklch(0.1908 0.0020 106.5859)',
    '--destructive-foreground': 'oklch(1.0000 0 0)',
    '--border': 'oklch(0.8847 0.0069 97.3627)',
    '--input': 'oklch(0.7621 0.0156 98.3528)',
    '--ring': 'oklch(0.6171 0.1375 39.0427)',
    '--sidebar': 'oklch(0.9663 0.0080 98.8792)',
    '--sidebar-foreground': 'oklch(0.3590 0.0051 106.6524)',
    '--sidebar-primary': 'oklch(0.6171 0.1375 39.0427)',
    '--sidebar-primary-foreground': 'oklch(0.9881 0 0)',
    '--sidebar-accent': 'oklch(0.9245 0.0138 92.9892)',
    '--sidebar-accent-foreground': 'oklch(0.3250 0 0)',
    '--sidebar-border': 'oklch(0.9401 0 0)',
    '--sidebar-ring': 'oklch(0.7731 0 0)',
  },
  dark: {
    '--background': 'oklch(0.2679 0.0036 106.6427)',
    '--foreground': 'oklch(0.8074 0.0142 93.0137)',
    '--card': 'oklch(0.2679 0.0036 106.6427)',
    '--card-foreground': 'oklch(0.9818 0.0054 95.0986)',
    '--popover': 'oklch(0.3085 0.0035 106.6039)',
    '--popover-foreground': 'oklch(0.9211 0.0040 106.4781)',
    '--primary': 'oklch(0.6724 0.1308 38.7559)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.9818 0.0054 95.0986)',
    '--secondary-foreground': 'oklch(0.3085 0.0035 106.6039)',
    '--muted': 'oklch(0.2213 0.0038 106.7070)',
    '--muted-foreground': 'oklch(0.7713 0.0169 99.0657)',
    '--accent': 'oklch(0.2130 0.0078 95.4245)',
    '--accent-foreground': 'oklch(0.9663 0.0080 98.8792)',
    '--destructive': 'oklch(0.6368 0.2078 25.3313)',
    '--destructive-foreground': 'oklch(1.0000 0 0)',
    '--border': 'oklch(0.3618 0.0101 106.8928)',
    '--input': 'oklch(0.4336 0.0113 100.2195)',
    '--ring': 'oklch(0.6724 0.1308 38.7559)',
    '--sidebar': 'oklch(0.2357 0.0024 67.7077)',
    '--sidebar-foreground': 'oklch(0.8074 0.0142 93.0137)',
    '--sidebar-primary': 'oklch(0.3250 0 0)',
    '--sidebar-primary-foreground': 'oklch(0.9881 0 0)',
    '--sidebar-accent': 'oklch(0.1680 0.0020 106.6177)',
    '--sidebar-accent-foreground': 'oklch(0.8074 0.0142 93.0137)',
    '--sidebar-border': 'oklch(0.3618 0.0101 106.8928)',
    '--sidebar-ring': 'oklch(0.7731 0 0)',
  },
}

// 중성 테마 (회색 계열)
const neutralTheme: ThemeColors = {
  light: {
    '--background': 'oklch(0.98 0.002 0)',
    '--foreground': 'oklch(0.15 0.005 0)',
    '--card': 'oklch(0.985 0.003 0)',
    '--card-foreground': 'oklch(0.15 0.005 0)',
    '--popover': 'oklch(0.99 0.002 0)',
    '--popover-foreground': 'oklch(0.15 0.005 0)',
    '--primary': 'oklch(0.45 0.02 220)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.94 0.01 0)',
    '--secondary-foreground': 'oklch(0.15 0.01 0)',
    '--muted': 'oklch(0.95 0.01 0)',
    '--muted-foreground': 'oklch(0.35 0.01 0)',
    '--accent': 'oklch(0.92 0.015 0)',
    '--accent-foreground': 'oklch(0.1 0.01 0)',
    '--destructive': 'oklch(0.65 0.25 15)',
    '--destructive-foreground': 'oklch(0.98 0.002 0)',
    '--border': 'oklch(0.85 0.01 0)',
    '--input': 'oklch(0.97 0.005 0)',
    '--ring': 'oklch(0.45 0.02 220)',
    '--sidebar': 'oklch(0.985 0.003 0)',
    '--sidebar-foreground': 'oklch(0.15 0.005 0)',
    '--sidebar-primary': 'oklch(0.45 0.02 220)',
    '--sidebar-primary-foreground': 'oklch(1.0000 0 0)',
    '--sidebar-accent': 'oklch(0.92 0.015 0)',
    '--sidebar-accent-foreground': 'oklch(0.1 0.01 0)',
    '--sidebar-border': 'oklch(0.88 0.01 0)',
    '--sidebar-ring': 'oklch(0.45 0.02 220)',
  },
  dark: {
    '--background': 'oklch(0.15 0.005 0)',
    '--foreground': 'oklch(0.92 0.002 0)',
    '--card': 'oklch(0.18 0.005 0)',
    '--card-foreground': 'oklch(0.92 0.002 0)',
    '--popover': 'oklch(0.16 0.005 0)',
    '--popover-foreground': 'oklch(0.92 0.002 0)',
    '--primary': 'oklch(0.65 0.03 220)',
    '--primary-foreground': 'oklch(1.0000 0 0)',
    '--secondary': 'oklch(0.2 0.005 0)',
    '--secondary-foreground': 'oklch(0.92 0.002 0)',
    '--muted': 'oklch(0.22 0.01 0)',
    '--muted-foreground': 'oklch(0.75 0.01 0)',
    '--accent': 'oklch(0.25 0.015 0)',
    '--accent-foreground': 'oklch(0.88 0.005 0)',
    '--destructive': 'oklch(0.6368 0.2078 25.3313)',
    '--destructive-foreground': 'oklch(1.0000 0 0)',
    '--border': 'oklch(0.3 0.01 0)',
    '--input': 'oklch(0.25 0.01 0)',
    '--ring': 'oklch(0.65 0.03 220)',
    '--sidebar': 'oklch(0.17 0.005 0)',
    '--sidebar-foreground': 'oklch(0.92 0.002 0)',
    '--sidebar-primary': 'oklch(0.65 0.03 220)',
    '--sidebar-primary-foreground': 'oklch(1.0000 0 0)',
    '--sidebar-accent': 'oklch(0.25 0.015 0)',
    '--sidebar-accent-foreground': 'oklch(0.88 0.005 0)',
    '--sidebar-border': 'oklch(0.28 0.01 0)',
    '--sidebar-ring': 'oklch(0.65 0.03 220)',
  },
}

const themes: Record<ThemeName, ThemeColors> = {
  default: defaultTheme,
  warm: warmTheme,
  neutral: neutralTheme,
}

const themeNames: Record<ThemeName, string> = {
  default: '기본 (오렌지)',
  warm: '따뜻한 (브라운)',
  neutral: '중성 (그레이)',
}

// 다크 모드 상태
const isDark = ref(false)
const currentTheme = ref<ThemeName>('default')

// localStorage에서 테마 설정 읽기
const THEME_STORAGE_KEY = 'nsales-theme'
const DARK_MODE_STORAGE_KEY = 'nsales-dark-mode'

const initializeTheme = () => {
  // localStorage에서 테마 설정 읽기
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeName
  if (savedTheme && themes[savedTheme]) {
    currentTheme.value = savedTheme
  }

  const savedDarkMode = localStorage.getItem(DARK_MODE_STORAGE_KEY)
  if (savedDarkMode) {
    isDark.value = JSON.parse(savedDarkMode)
  } else {
    // 시스템 기본 설정 감지
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  // 시스템 테마 변경 감지
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(DARK_MODE_STORAGE_KEY)) {
      isDark.value = e.matches
    }
  })
}

const applyTheme = (themeName: ThemeName, dark: boolean) => {
  const theme = themes[themeName]
  const colors = dark ? theme.dark : theme.light
  
  // CSS 변수 적용
  Object.entries(colors).forEach(([property, value]) => {
    document.documentElement.style.setProperty(property, value)
  })

  // HTML 클래스 토글
  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export function useTheme() {
  let isInitialized = false

  // 테마나 다크 모드 변경 시 적용
  watch([currentTheme, isDark], ([theme, dark]) => {
    if (isInitialized) {
      applyTheme(theme, dark)
      localStorage.setItem(THEME_STORAGE_KEY, theme)
      localStorage.setItem(DARK_MODE_STORAGE_KEY, JSON.stringify(dark))
    }
  })

  // 테마 전환 함수들
  const setTheme = (themeName: ThemeName) => {
    currentTheme.value = themeName
  }

  const toggleDarkMode = () => {
    isDark.value = !isDark.value
  }

  const setDarkMode = (dark: boolean) => {
    isDark.value = dark
  }

  // 초기화 개선
  const enhancedInitializeTheme = () => {
    // localStorage에서 테마 설정 읽기
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeName
    if (savedTheme && themes[savedTheme]) {
      currentTheme.value = savedTheme
    }

    const savedDarkMode = localStorage.getItem(DARK_MODE_STORAGE_KEY)
    if (savedDarkMode) {
      isDark.value = JSON.parse(savedDarkMode)
    } else {
      // 시스템 기본 설정 감지
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }

    // 시스템 테마 변경 감지
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(DARK_MODE_STORAGE_KEY)) {
        isDark.value = e.matches
      }
    })

    // 초기 테마 적용
    applyTheme(currentTheme.value, isDark.value)
    isInitialized = true
  }

  // computed 속성들
  const themeOptions = computed(() => 
    Object.entries(themeNames).map(([key, name]) => ({
      value: key as ThemeName,
      label: name,
    }))
  )

  const currentThemeName = computed(() => themeNames[currentTheme.value])

  return {
    // 상태
    isDark: computed(() => isDark.value),
    currentTheme: computed(() => currentTheme.value),
    currentThemeName,
    themeOptions,
    
    // 메서드
    setTheme,
    toggleDarkMode,
    setDarkMode,
    initializeTheme: enhancedInitializeTheme,
    
    // 상수
    themeNames,
  }
}
