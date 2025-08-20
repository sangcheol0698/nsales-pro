<template>
  <div class="w-full">
    <div class="flex items-center py-4">
      <Input
        placeholder="Search orders..."
        v-model="searchQuery"
        class="max-w-sm"
      />
      <div class="ml-auto flex items-center space-x-2">
        <Button variant="outline" size="sm" @click="exportData">
          <Download class="mr-2 h-4 w-4" />
          Export
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="outline" size="sm">
              Status
              <ChevronDown class="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuCheckboxItem
              v-for="status in statuses"
              :key="status.value"
              :checked="selectedStatuses.includes(status.value)"
              @checked-change="(checked) => toggleStatus(status.value, checked)"
            >
              {{ status.label }}
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
    <div class="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <Checkbox
                :checked="isAllSelected"
                @update:checked="toggleAll"
                aria-label="Select all"
              />
            </TableHead>
            <TableHead class="w-[100px]">Order ID</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            <TableHead class="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="order in paginatedOrders"
            :key="order.id"
            :class="selectedOrders.includes(order.id) ? 'bg-muted/50' : ''"
          >
            <TableCell>
              <Checkbox
                :checked="selectedOrders.includes(order.id)"
                @update:checked="(checked) => toggleOrder(order.id, checked)"
                :aria-label="`Select order ${order.id}`"
              />
            </TableCell>
            <TableCell class="font-medium">{{ order.id }}</TableCell>
            <TableCell>{{ order.customer }}</TableCell>
            <TableCell>
              <Badge :variant="getStatusVariant(order.status)">
                {{ order.status }}
              </Badge>
            </TableCell>
            <TableCell>{{ formatDate(order.date) }}</TableCell>
            <TableCell class="text-right">{{ order.amount }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
    <div class="flex items-center justify-between space-x-2 py-4">
      <div class="flex-1 text-sm text-muted-foreground">
        {{ selectedOrders.length }} of {{ filteredOrders.length }} order(s) selected.
      </div>
      <div class="flex items-center space-x-6 lg:space-x-8">
        <div class="flex items-center space-x-2">
          <p class="text-sm font-medium">Rows per page</p>
          <Select v-model="pageSize">
            <SelectTrigger class="h-8 w-[70px]">
              <SelectValue :placeholder="pageSize" />
            </SelectTrigger>
            <SelectContent side="top">
              <SelectItem v-for="size in pageSizeOptions" :key="size" :value="size">
                {{ size }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex w-[100px] items-center justify-center text-sm font-medium">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <div class="flex items-center space-x-2">
          <Button
            variant="outline"
            class="hidden h-8 w-8 p-0 lg:flex"
            @click="goToPage(1)"
            :disabled="currentPage === 1"
          >
            <ChevronsLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            class="h-8 w-8 p-0"
            @click="previousPage"
            :disabled="currentPage === 1"
          >
            <ChevronLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            class="h-8 w-8 p-0"
            @click="nextPage"
            :disabled="currentPage === totalPages"
          >
            <ChevronRight class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            class="hidden h-8 w-8 p-0 lg:flex"
            @click="goToPage(totalPages)"
            :disabled="currentPage === totalPages"
          >
            <ChevronsRight class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Download,
} from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface Order {
  id: string
  customer: string
  status: string
  amount: string
  date: string
}

const props = defineProps<{
  orders: Order[]
}>()

const searchQuery = ref('')
const selectedOrders = ref<string[]>([])
const selectedStatuses = ref(['completed', 'pending', 'processing', 'cancelled'])
const currentPage = ref(1)
const pageSize = ref(10)

const statuses = [
  { value: 'completed', label: 'Completed' },
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
  { value: 'cancelled', label: 'Cancelled' },
]

const pageSizeOptions = [5, 10, 20, 30, 40, 50]

const filteredOrders = computed(() => {
  return props.orders.filter(order => {
    const matchesSearch = order.customer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         order.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = selectedStatuses.value.includes(order.status)
    return matchesSearch && matchesStatus
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredOrders.value.length / pageSize.value)
})

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOrders.value.slice(start, end)
})

const isAllSelected = computed(() => {
  return paginatedOrders.value.length > 0 && 
         paginatedOrders.value.every(order => selectedOrders.value.includes(order.id))
})

const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
  switch (status) {
    case 'completed':
      return 'default'
    case 'pending':
      return 'secondary'
    case 'processing':
      return 'outline'
    case 'cancelled':
      return 'destructive'
    default:
      return 'outline'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const toggleOrder = (orderId: string, checked: boolean) => {
  if (checked) {
    selectedOrders.value.push(orderId)
  } else {
    selectedOrders.value = selectedOrders.value.filter(id => id !== orderId)
  }
}

const toggleAll = (checked: boolean) => {
  if (checked) {
    selectedOrders.value = [...paginatedOrders.value.map(order => order.id)]
  } else {
    selectedOrders.value = []
  }
}

const toggleStatus = (status: string, checked: boolean) => {
  if (checked) {
    selectedStatuses.value.push(status)
  } else {
    selectedStatuses.value = selectedStatuses.value.filter(s => s !== status)
  }
  currentPage.value = 1 // Reset to first page when filtering
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const goToPage = (page: number) => {
  currentPage.value = Math.max(1, Math.min(page, totalPages.value))
}

const exportData = () => {
  const dataToExport = selectedOrders.value.length > 0 
    ? props.orders.filter(order => selectedOrders.value.includes(order.id))
    : filteredOrders.value
  
  const csvContent = [
    'Order ID,Customer,Status,Amount,Date',
    ...dataToExport.map(order => 
      `${order.id},${order.customer},${order.status},${order.amount},${order.date}`
    )
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'orders.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

// Reset page when search changes
watch(searchQuery, () => {
  currentPage.value = 1
})

// Reset page when page size changes
watch(pageSize, () => {
  currentPage.value = 1
})
</script>