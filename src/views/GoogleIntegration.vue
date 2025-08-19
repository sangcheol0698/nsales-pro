<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="google-integration-page">
        <!-- 페이지 헤더 -->
        <div class="mb-8">
          <div class="flex items-center gap-3 mb-4">
            <div
              class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
            </div>
            <div>
              <h1 class="text-3xl font-bold text-foreground">Google 서비스 연동</h1>
              <p class="text-muted-foreground">AI와 함께 Google Calendar 및 Gmail을 효율적으로 사용하세요</p>
            </div>
          </div>
        </div>

        <div class="grid lg:grid-cols-3 gap-8">
          <!-- 메인 콘텐츠 -->
          <div class="lg:col-span-2 space-y-8">
            <!-- 연동 상태 카드 -->
            <div class="bg-card border rounded-xl p-6">
              <GoogleStatus />
            </div>

            <!-- 기능 소개 카드 -->
            <div class="bg-card border rounded-xl p-6 space-y-6">
              <div>
                <h2 class="text-xl font-semibold text-foreground mb-2">✨ AI로 더 스마트한 업무 관리</h2>
                <p class="text-muted-foreground">자연어로 일정 관리와 이메일 작업을 쉽게 처리하세요</p>
              </div>

              <!-- 기능 리스트 -->
              <div class="grid md:grid-cols-2 gap-4">
                <!-- 캘린더 기능 -->
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                      <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z" />
                      </svg>
                    </div>
                    <h3 class="font-medium text-foreground">📅 캘린더 관리</h3>
                  </div>
                  <ul class="space-y-2 text-sm text-muted-foreground ml-11">
                    <li>• 일정 확인 및 검색</li>
                    <li>• 새 일정 생성</li>
                    <li>• 일정 수정 및 삭제</li>
                    <li>• 빈 시간 찾기</li>
                  </ul>
                </div>

                <!-- 이메일 기능 -->
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                      <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
                      </svg>
                    </div>
                    <h3 class="font-medium text-foreground">📧 Gmail 관리</h3>
                  </div>
                  <ul class="space-y-2 text-sm text-muted-foreground ml-11">
                    <li>• 이메일 검색 및 조회</li>
                    <li>• 이메일 작성 및 발송</li>
                    <li>• 중요 메일 필터링</li>
                    <li>• 자동 답장 생성</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- AI 명령어 예시 -->
            <div class="bg-card border rounded-xl p-6 space-y-6">
              <div>
                <h2 class="text-xl font-semibold text-foreground mb-2">🎯 AI 명령어 예시</h2>
                <p class="text-muted-foreground">이런 식으로 AI에게 요청해보세요</p>
              </div>

              <div class="space-y-4">
                <!-- 캘린더 예시 -->
                <div>
                  <h3 class="font-medium text-foreground mb-3 flex items-center gap-2">
                    <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                    캘린더 관련
                  </h3>
                  <div class="grid gap-2">
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "오늘 일정 확인해줘"
                    </div>
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "내일 오후 3시에 팀 미팅 일정 잡아줘"
                    </div>
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "다음 주 화요일 2시간 회의 가능한 시간 찾아줘"
                    </div>
                  </div>
                </div>

                <!-- 이메일 예시 -->
                <div>
                  <h3 class="font-medium text-foreground mb-3 flex items-center gap-2">
                    <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                    이메일 관련
                  </h3>
                  <div class="grid gap-2">
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "김과장님께 회의 일정 메일 보내줘"
                    </div>
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "최근 받은 중요한 메일 확인해줘"
                    </div>
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "프로젝트 관련 메일 찾아서 요약해줘"
                    </div>
                  </div>
                </div>

                <!-- 통합 작업 예시 -->
                <div>
                  <h3 class="font-medium text-foreground mb-3 flex items-center gap-2">
                    <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
                    통합 작업
                  </h3>
                  <div class="grid gap-2">
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "내일 일정 확인하고 김대리님께 빈 시간 알려주는 메일 보내줘"
                    </div>
                    <div class="p-3 bg-muted/50 rounded-lg font-mono text-sm">
                      "회의실 예약하고 참석자들에게 알림 메일 발송해줘"
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 사이드바 -->
          <div class="space-y-6">
            <!-- 빠른 설정 -->
            <div class="bg-card border rounded-xl p-6 space-y-4">
              <h3 class="font-semibold text-foreground">⚡ 빠른 설정</h3>

              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-foreground">서비스 알림</span>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" v-model="notificationsEnabled">
                    <div
                      class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div class="flex items-center justify-between">
                  <span class="text-sm text-foreground">자동 동기화</span>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" v-model="autoSyncEnabled">
                    <div
                      class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>

            <!-- 도움말 -->
            <div class="bg-card border rounded-xl p-6 space-y-4">
              <h3 class="font-semibold text-foreground">📖 도움말</h3>

              <div class="space-y-3">
                <button class="w-full text-left p-3 rounded-lg hover:bg-accent transition-colors">
                  <div class="font-medium text-sm">설정 가이드</div>
                  <div class="text-xs text-muted-foreground">Google Cloud Console 설정</div>
                </button>

                <button class="w-full text-left p-3 rounded-lg hover:bg-accent transition-colors">
                  <div class="font-medium text-sm">보안 정보</div>
                  <div class="text-xs text-muted-foreground">개인정보 보호 정책</div>
                </button>

                <button class="w-full text-left p-3 rounded-lg hover:bg-accent transition-colors">
                  <div class="font-medium text-sm">문제 해결</div>
                  <div class="text-xs text-muted-foreground">자주 묻는 질문</div>
                </button>
              </div>
            </div>

            <!-- 상태 정보 -->
            <div class="bg-card border rounded-xl p-6 space-y-4">
              <h3 class="font-semibold text-foreground">📊 연동 상태</h3>

              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-muted-foreground">Google API</span>
                  <span
                    class="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded-full">
                활성
              </span>
                </div>

                <div class="flex items-center justify-between">
                  <span class="text-sm text-muted-foreground">캘린더 권한</span>
                  <span
                    class="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded-full">
                허용됨
              </span>
                </div>

                <div class="flex items-center justify-between">
                  <span class="text-sm text-muted-foreground">Gmail 권한</span>
                  <span
                    class="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded-full">
                허용됨
              </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GoogleStatus from '@/components/GoogleStatus.vue';
import { SidebarLayout } from '@/components/layout';

// 설정 상태
const notificationsEnabled = ref(true);
const autoSyncEnabled = ref(true);
</script>

<style scoped>
.google-integration-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.5rem;
}
</style>