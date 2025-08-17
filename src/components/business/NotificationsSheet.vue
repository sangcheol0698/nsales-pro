<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[380px] sm:w-[420px] p-0" :show-close="false">
      <div class="flex items-center justify-between px-4 py-3 border-b">
        <div class="flex items-center gap-2">
          <Bell class="h-4 w-4" />
          <h3 class="font-semibold">알림</h3>
          <Badge v-if="unreadCount > 0" variant="destructive" class="ml-1">{{ unreadCount }}</Badge>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="ghost" size="sm" class="h-8 px-2" :disabled="unreadCount === 0" @click="markAllAsRead">
            모두 읽음처리
          </Button>
          <Button variant="ghost" size="icon" class="h-8 w-8" :disabled="items.length === 0" @click="clearAll">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div class="p-3">
        <div class="flex items-center gap-2 mb-2">
          <Button size="sm" variant="outline" :class="tab === 'all' ? 'bg-accent' : ''" @click="tab = 'all'">전체</Button>
          <Button size="sm" variant="outline" :class="tab === 'unread' ? 'bg-accent' : ''" @click="tab = 'unread'">안읽음
          </Button>
        </div>

        <div v-if="filtered.length === 0" class="py-10 text-center text-sm text-muted-foreground">
          표시할 알림이 없습니다.
        </div>

        <ul v-else class="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
          <li v-for="n in filtered" :key="n.id">
            <button class="w-full text-left rounded-md px-3 py-2 hover:bg-accent/60 focus:bg-accent/60"
                    @click="onClickItem(n)">
              <div class="flex items-start gap-3">
                <div class="mt-0.5">
                  <span :class="iconClass(n.type)"></span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <p class="font-medium truncate">{{ n.title }}</p>
                    <span v-if="!n.read" class="inline-block h-2 w-2 rounded-full bg-primary"></span>
                  </div>
                  <p v-if="n.body" class="text-sm text-muted-foreground line-clamp-2">{{ n.body }}</p>
                  <p class="mt-1 text-[11px] text-muted-foreground">{{ formatTime(n.createdAt) }}</p>
                </div>
              </div>
            </button>
          </li>
        </ul>

        <div class="mt-3">
          <Button variant="outline" class="w-full" @click="goAll">모든 알림 보기</Button>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Bell, Trash2 } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { type NotificationItem, useNotificationsStore } from '@/core/stores/notifications.store';

const { open } = defineProps<{ open: boolean }>();
const emit = defineEmits<{ 'update:open': [boolean] }>();

const router = useRouter();
const store = useNotificationsStore();
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

async function onClickItem(n: NotificationItem) {
  store.markAsRead(n.id);
  if (n.link) {
    await router.push(n.link);
  }
  emit('update:open', false);
}

function goAll() {
  router.push('/notifications');
  emit('update:open', false);
}
</script>
