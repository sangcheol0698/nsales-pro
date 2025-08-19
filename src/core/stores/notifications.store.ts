import { defineStore } from 'pinia';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface NotificationItem {
  id: string;
  title: string;
  body?: string;
  type: NotificationType;
  createdAt: string; // ISO string
  read: boolean;
  link?: string; // optional deep link
}

function nowMinus(minutes: number) {
  const d = new Date(Date.now() - minutes * 60 * 1000);
  return d.toISOString();
}

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [
      {
        id: 'n1',
        title: '새 프로젝트가 등록되었습니다',
        body: '프로젝트 \'Abacus 차세대\'가 생성되었어요.',
        type: 'info' as NotificationType,
        createdAt: nowMinus(5),
        read: false,
        link: '/projects',
      },
      {
        id: 'n2',
        title: '오늘 마감 일정 알림',
        body: '견적 제출 마감 2시간 전입니다.',
        type: 'warning' as NotificationType,
        createdAt: nowMinus(35),
        read: false,
      },
      {
        id: 'n3',
        title: '수금 완료',
        body: 'ABC 고객사의 2차 대금이 입금되었습니다.',
        type: 'success' as NotificationType,
        createdAt: nowMinus(120),
        read: true,
        link: '/sales',
      },
    ] as NotificationItem[],
  }),
  getters: {
    unreadCount: (state) => state.items.filter((n) => !n.read).length,
    sorted: (state) =>
      [...state.items].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()),
  },
  actions: {
    markAsRead(id: string) {
      const n = this.items.find((x) => x.id === id);
      if (n) n.read = true;
    },
    markAllAsRead() {
      this.items.forEach((n) => (n.read = true));
    },
    addNotification(partial: Omit<NotificationItem, 'id' | 'createdAt' | 'read'> & {
      id?: string;
      createdAt?: string;
      read?: boolean
    }) {
      const id = partial.id ?? `n${Math.random().toString(36).slice(2, 9)}`;
      const createdAt = partial.createdAt ?? new Date().toISOString();
      const read = partial.read ?? false;
      this.items.unshift({ ...partial, id, createdAt, read });
    },
    clearAll() {
      this.items = [];
    },
  },
});

