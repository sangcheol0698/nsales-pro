<template>
  <div class="fixed top-4 right-4 z-50">
    <Card class="w-64">
      <CardHeader class="pb-2">
        <CardTitle class="text-sm">개발용 권한 전환</CardTitle>
      </CardHeader>
      <CardContent class="space-y-3">
        <div class="space-y-2">
          <p class="text-xs text-muted-foreground">
            현재 사용자: <span class="font-medium">{{ user?.name || '없음' }}</span>
          </p>
          <p class="text-xs text-muted-foreground">
            권한: <span class="font-medium" :class="isAdmin ? 'text-blue-600' : 'text-gray-600'">
              {{ user?.role === 'ADMIN' ? '관리자' : user?.role === 'USER' ? '일반사용자' : '없음' }}
            </span>
          </p>
        </div>
        
        <Separator />
        
        <div class="space-y-2">
          <Button 
            @click="setAdmin" 
            size="sm" 
            variant="outline"
            :class="isAdmin ? 'bg-blue-50 border-blue-200 text-blue-700' : ''"
            class="w-full justify-start"
          >
            <Crown class="h-4 w-4 mr-2" />
            관리자로 전환
          </Button>
          
          <Button 
            @click="setUser" 
            size="sm" 
            variant="outline"
            :class="!isAdmin && user ? 'bg-gray-50 border-gray-200 text-gray-700' : ''"
            class="w-full justify-start"
          >
            <User class="h-4 w-4 mr-2" />
            일반사용자로 전환
          </Button>
        </div>
        
        <div class="text-xs text-muted-foreground">
          권한을 변경한 후 페이지가 자동으로 새로고침됩니다.
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Crown, User } from 'lucide-vue-next';

import { useAuth } from '@/core/composables/useAuth';

const { user, isAdmin } = useAuth();

const setAdmin = () => {
  const adminUser = {
    name: '관리자',
    username: 'admin',
    role: 'ADMIN'
  };
  
  localStorage.setItem('user', JSON.stringify(adminUser));
  window.location.reload();
};

const setUser = () => {
  const regularUser = {
    name: '일반사용자',
    username: 'user',
    role: 'USER'
  };
  
  localStorage.setItem('user', JSON.stringify(regularUser));
  window.location.reload();
};
</script>