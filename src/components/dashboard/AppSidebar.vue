<template>
  <Sidebar collapsible="icon">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <a href="#">
              <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <Command class="size-4" />
              </div>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">Acme Inc</span>
                <span class="truncate text-xs">Enterprise</span>
              </div>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="data.navMain" />
      <NavProjects :projects="data.projects" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser :user="data.user" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>

<script setup lang="ts">
import { Command } from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import NavMain from './nav-main.vue'
import NavProjects from './nav-projects.vue'
import NavUser from './nav-user.vue'

// This is sample data.
const data = {
  user: {
    name: 'shadcn',
    email: 'm@example.com',
    avatar: '/avatars/shadcn.jpg',
  },
  navMain: [
    {
      title: 'Dashboard',
      url: '#',
      icon: 'LayoutDashboard',
      isActive: true,
      items: [
        {
          title: 'Overview',
          url: '#',
        },
        {
          title: 'Analytics',
          url: '#',
        },
        {
          title: 'Reports',
          url: '#',
        },
      ],
    },
    {
      title: 'Sales',
      url: '#',
      icon: 'ShoppingCart',
      items: [
        {
          title: 'Orders',
          url: '#',
        },
        {
          title: 'Products',
          url: '#',
        },
        {
          title: 'Customers',
          url: '#',
        },
      ],
    },
    {
      title: 'Finance',
      url: '#',
      icon: 'DollarSign',
      items: [
        {
          title: 'Revenue',
          url: '#',
        },
        {
          title: 'Expenses',
          url: '#',
        },
        {
          title: 'Budgets',
          url: '#',
        },
      ],
    },
    {
      title: 'Team',
      url: '#',
      icon: 'Users',
      items: [
        {
          title: 'Members',
          url: '#',
        },
        {
          title: 'Roles',
          url: '#',
        },
        {
          title: 'Permissions',
          url: '#',
        },
      ],
    },
    {
      title: 'Settings',
      url: '#',
      icon: 'Settings2',
      items: [
        {
          title: 'General',
          url: '#',
        },
        {
          title: 'Security',
          url: '#',
        },
        {
          title: 'Billing',
          url: '#',
        },
      ],
    },
  ],
  projects: [
    {
      name: 'Design Engineering',
      url: '#',
      icon: 'Frame',
    },
    {
      name: 'Sales & Marketing',
      url: '#',
      icon: 'PieChart',
    },
    {
      name: 'Travel',
      url: '#',
      icon: 'Map',
    },
  ],
}
</script>