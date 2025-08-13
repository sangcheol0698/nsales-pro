<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside class="hidden w-64 flex-shrink-0 bg-background border-r md:flex md:flex-col">
      <div class="flex h-16 items-center px-4 border-b">
        <router-link to="/" class="flex items-center space-x-2">
          <h1 class="text-xl font-bold">ABACUS</h1>
        </router-link>
      </div>

      <nav class="flex-1 space-y-1 p-4">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent hover:text-accent-foreground"
          :class="{ 'bg-accent text-accent-foreground': $route.path.startsWith(item.path) }"
        >
          <component :is="item.icon" class="h-4 w-4"/>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Header -->
      <header class="h-16 bg-background border-b flex items-center justify-between px-4">
        <div class="flex items-center space-x-4">
          <!-- Mobile menu button -->
          <Button variant="ghost" size="sm" class="md:hidden">
            <Menu class="h-4 w-4"/>
          </Button>
        </div>

        <div class="flex items-center space-x-4">
          <!-- User menu -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="sm">
                <User class="h-4 w-4"/>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>프로필</DropdownMenuItem>
              <DropdownMenuItem>설정</DropdownMenuItem>
              <DropdownMenuSeparator/>
              <DropdownMenuItem>로그아웃</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <!-- Main content area -->
      <main class="flex-1 overflow-auto">
        <slot/>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Building, FolderOpen, Menu, MessageSquare, PieChart, User, Users } from 'lucide-vue-next';
  import { Button } from '@/components/ui/button';
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu';

  const navigation = [
    { name: '직원', path: '/employees', icon: Users },
    { name: '프로젝트', path: '/projects', icon: FolderOpen },
    { name: '협력사', path: '/partners', icon: Building },
    { name: '채팅', path: '/chat', icon: MessageSquare },
    { name: '대시보드', path: '/dashboard', icon: PieChart },
  ];
</script>
