<template>
  <SidebarGroup>
    <SidebarGroupLabel>Platform</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <Collapsible
          v-if="item.items"
          :open="item.isActive"
          class="group/collapsible"
        >
          <SidebarMenuButton
            as-child
            :tooltip="item.title"
          >
            <CollapsibleTrigger>
              <component :is="getIcon(item.icon)" />
              <span>{{ item.title }}</span>
              <ChevronRight class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
            </CollapsibleTrigger>
          </SidebarMenuButton>
          <CollapsibleContent>
            <SidebarMenuSub>
              <SidebarMenuSubItem v-for="subItem in item.items" :key="subItem.title">
                <SidebarMenuSubButton as-child>
                  <a :href="subItem.url">
                    <span>{{ subItem.title }}</span>
                  </a>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            </SidebarMenuSub>
          </CollapsibleContent>
        </Collapsible>
        <SidebarMenuButton v-else as-child :tooltip="item.title">
          <a :href="item.url">
            <component :is="getIcon(item.icon)" />
            <span>{{ item.title }}</span>
          </a>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  </SidebarGroup>
</template>

<script setup lang="ts">
import { ChevronRight, LayoutDashboard, ShoppingCart, DollarSign, Users, Settings2 } from 'lucide-vue-next'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@/components/ui/sidebar'

interface NavItem {
  title: string
  url: string
  icon: string
  isActive?: boolean
  items?: {
    title: string
    url: string
  }[]
}

defineProps<{
  items: NavItem[]
}>()

const getIcon = (iconName: string) => {
  const icons: Record<string, any> = {
    LayoutDashboard,
    ShoppingCart,
    DollarSign,
    Users,
    Settings2,
  }
  return icons[iconName] || LayoutDashboard
}
</script>