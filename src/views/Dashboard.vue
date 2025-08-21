<template>
  <div class="min-h-screen bg-gray-50/40">
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header class="flex h-16 shrink-0 items-center gap-2">
          <div class="flex items-center gap-2 px-4">
            <SidebarTrigger class="-ml-1" />
            <Separator orientation="vertical" class="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem class="hidden md:block">
                  <BreadcrumbLink href="#">Dashboard</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator class="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Overview</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div class="ml-auto px-4">
            <Button @click="refreshData" :disabled="isLoading" variant="outline" size="sm">
              <RefreshCw :class="{ 'animate-spin': isLoading }" class="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </header>
        
        <div class="flex flex-1 flex-col gap-4 p-4 pt-0">
          <!-- Stats Cards -->
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card v-for="stat in dashboardData.stats" :key="stat.title">
              <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">{{ stat.title }}</CardTitle>
                <DollarSign v-if="stat.title.includes('Revenue')" class="h-4 w-4 text-muted-foreground" />
                <Users v-else-if="stat.title.includes('Subscriptions')" class="h-4 w-4 text-muted-foreground" />
                <CreditCard v-else-if="stat.title.includes('Sales')" class="h-4 w-4 text-muted-foreground" />
                <Activity v-else class="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div class="text-2xl font-bold">{{ stat.value }}</div>
                <p class="text-xs text-muted-foreground">
                  <span :class="stat.trend === 'up' ? 'text-green-600' : 'text-red-600'">
                    {{ stat.change }}
                  </span>
                  from last month
                </p>
              </CardContent>
            </Card>
          </div>

          <!-- Main Content Grid -->
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <!-- Revenue Chart -->
            <Card class="col-span-4">
              <CardHeader>
                <CardTitle>Revenue Overview</CardTitle>
              </CardHeader>
              <CardContent class="pl-2">
                <RevenueChart />
              </CardContent>
            </Card>
            
            <!-- Recent Sales -->
            <Card class="col-span-3">
              <CardHeader>
                <CardTitle>Recent Sales</CardTitle>
                <CardDescription>
                  You made {{ dashboardData.recentSales.length }} sales this month.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div class="space-y-8">
                  <div v-for="sale in dashboardData.recentSales" :key="sale.email" class="flex items-center">
                    <Avatar class="h-9 w-9">
                      <AvatarImage :src="`/avatars/${sale.name.toLowerCase().replace(/\s+/g, '-')}.jpg`" :alt="sale.name" />
                      <AvatarFallback>{{ sale.name.split(' ').map(n => n[0]).join('') }}</AvatarFallback>
                    </Avatar>
                    <div class="ml-4 space-y-1">
                      <p class="text-sm font-medium leading-none">{{ sale.name }}</p>
                      <p class="text-sm text-muted-foreground">{{ sale.email }}</p>
                    </div>
                    <div class="ml-auto font-medium">{{ sale.amount }}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Data Table -->
          <Card>
            <CardHeader>
              <CardTitle>Recent Orders</CardTitle>
              <CardDescription>
                A list of your recent orders with status and details.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <OrdersTable :orders="orders" />
            </CardContent>
          </Card>

          <!-- Analytics Grid -->
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">Conversion Rate</CardTitle>
                <TrendingUp class="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div class="text-2xl font-bold">3.24%</div>
                <div class="h-[80px] mt-4">
                  <ConversionChart />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">Top Products</CardTitle>
                <Package class="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div class="space-y-2">
                  <div v-for="product in topProducts" :key="product.name" class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                      <Badge variant="secondary">{{ product.rank }}</Badge>
                      <span class="text-sm">{{ product.name }}</span>
                    </div>
                    <span class="text-sm font-medium">${{ product.revenue }}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">Traffic Sources</CardTitle>
                <Globe class="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <TrafficChart />
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  Activity,
  CreditCard,
  DollarSign,
  Globe,
  Package,
  RefreshCw,
  TrendingUp,
  Users,
} from 'lucide-vue-next'
import AppSidebar from '@/components/dashboard/AppSidebar.vue'
import { 
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import RevenueChart from '@/components/dashboard/RevenueChart.vue'
import OrdersTable from '@/components/dashboard/OrdersTable.vue'
import ConversionChart from '@/components/dashboard/ConversionChart.vue'
import TrafficChart from '@/components/dashboard/TrafficChart.vue'

// Dashboard state
const dashboardData = ref({
  stats: [
    { title: 'Total Revenue', value: '$45,231.89', change: '+20.1%', trend: 'up' },
    { title: 'Subscriptions', value: '+2350', change: '+180.1%', trend: 'up' },
    { title: 'Sales', value: '+12,234', change: '+19%', trend: 'up' },
    { title: 'Active Now', value: '+573', change: '+201', trend: 'up' },
  ],
  recentSales: [
    { name: 'Olivia Martin', email: 'olivia.martin@email.com', amount: '+$1,999.00' },
    { name: 'Jackson Lee', email: 'jackson.lee@email.com', amount: '+$39.00' },
    { name: 'Isabella Nguyen', email: 'isabella.nguyen@email.com', amount: '+$299.00' },
    { name: 'William Kim', email: 'will@email.com', amount: '+$99.00' },
    { name: 'Sofia Davis', email: 'sofia.davis@email.com', amount: '+$39.00' },
  ]
})

const orders = ref([
  {
    id: 'ORD-001',
    customer: 'John Doe',
    status: 'completed',
    amount: '$250.00',
    date: '2024-01-15'
  },
  {
    id: 'ORD-002',
    customer: 'Jane Smith',
    status: 'pending',
    amount: '$150.00',
    date: '2024-01-14'
  },
  {
    id: 'ORD-003',
    customer: 'Bob Johnson',
    status: 'processing',
    amount: '$75.00',
    date: '2024-01-13'
  },
  {
    id: 'ORD-004',
    customer: 'Alice Brown',
    status: 'completed',
    amount: '$300.00',
    date: '2024-01-12'
  },
  {
    id: 'ORD-005',
    customer: 'Charlie Wilson',
    status: 'cancelled',
    amount: '$125.00',
    date: '2024-01-11'
  }
])

const topProducts = ref([
  { rank: '#1', name: 'Pro Plan', revenue: '12,345' },
  { rank: '#2', name: 'Basic Plan', revenue: '8,790' },
  { rank: '#3', name: 'Enterprise', revenue: '6,543' },
  { rank: '#4', name: 'Starter', revenue: '4,321' },
  { rank: '#5', name: 'Premium', revenue: '3,210' }
])

const isLoading = ref(false)

// Mock data refresh functionality
const refreshData = () => {
  isLoading.value = true
  setTimeout(() => {
    // Simulate data update
    dashboardData.value.stats = dashboardData.value.stats.map(stat => ({
      ...stat,
      value: stat.title === 'Total Revenue' ? 
        `$${(Math.random() * 50000 + 40000).toFixed(2)}` : 
        stat.value
    }))
    
    // Update orders
    orders.value = orders.value.map(order => ({
      ...order,
      amount: `$${(Math.random() * 500 + 50).toFixed(2)}`
    }))
    
    isLoading.value = false
  }, 1000)
}

// Auto refresh every 30 seconds
let refreshInterval: NodeJS.Timeout | null = null

onMounted(() => {
  refreshInterval = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>