<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full max-w-4xl mx-auto">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold">알림</h1>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" :disabled="unreadCount === 0" @click="markAllAsRead">
              모두 읽음 처리
            </Button>
            <Button variant="outline" size="sm" :disabled="items.length === 0" @click="clearAll">
              모두 지우기
            </Button>
          </div>
        </div>

        <div class="flex items-center gap-2 mb-3">
          <Button size="sm" variant="outline" :class="tab === 'all' ? 'bg-accent' : ''" @click="tab = 'all'">전체</Button>
          <Button size="sm" variant="outline" :class="tab === 'unread' ? 'bg-accent' : ''" @click="tab = 'unread'">안읽음
          </Button>
        </div>

        <Card>
          <CardContent class="p-0">
            <template v-if="filtered.length === 0">
              <div class="py-16 text-center text-muted-foreground">표시할 알림이 없습니다.</div>
            </template>
            <ul v-else class="divide-y">
              <li v-for="n in filtered" :key="n.id">
                <div class="flex gap-4 px-4 py-3 hover:bg-muted/40">
                  <div class="pt-1">
                    <span :class="iconClass(n.type)"></span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <p class="font-medium truncate">{{ n.title }}</p>
                      <Badge v-if="!n.read" variant="secondary">신규</Badge>
                    </div>
                    <p v-if="n.body" class="text-sm text-muted-foreground">{{ n.body }}</p>
                    <div class="mt-1 text-[11px] text-muted-foreground">{{ formatTime(n.createdAt) }}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <Button v-if="!n.read" size="sm" variant="ghost" @click="markAsRead(n.id)">읽음</Button>
                    <Button size="sm" variant="ghost" :disabled="!n.link" @click="go(n.link)">이동</Button>
                  </div>
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { SidebarLayout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { useNotificationsStore } from '@/core/stores/notifications.store';

const store = useNotificationsStore();
const router = useRouter();
const tab = ref<'all' | 'unread'>('all');

const items = computed(() => store.sorted);
const unreadCount = computed(() => store.unreadCount);
const filtered = computed(() => (tab.value === 'all' ? items.value : items.value.filter((n) => !n.read)));

function markAllAsRead() {
  store.markAllAsRead();
}

function clearAll() {
  store.clearAll();
}

function markAsRead(id: string) {
  store.markAsRead(id);
}

function go(link?: string) {
  if (!link) return;
  router.push(link);
}

function iconClass(type: string) {
  switch (type) {
    case 'success':
      return 'inline-block h-2.5 w-2.5 rounded-full bg-green-500';
    case 'warning':
      return 'inline-block h-2.5 w-2.5 rounded-full bg-yellow-500';
    case 'error':
      return 'inline-block h-2.5 w-2.5 rounded-full bg-red-500';
    default:
      return 'inline-block h-2.5 w-2.5 rounded-full bg-blue-500';
  }
}

function formatTime(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 60000);
  if (diff < 1) return '방금 전';
  if (diff < 60) return `${diff}분 전`;
  const h = Math.floor(diff / 60);
  if (h < 24) return `${h}시간 전`;
  const days = Math.floor(h / 24);
  return `${days}일 전`;
}
</script>

