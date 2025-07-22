<template>
  <div class="relative group">
    <!-- Card with gradient border animation -->
    <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 p-px opacity-75 group-hover:opacity-100 transition-all duration-500">
      <div class="h-full w-full rounded-xl bg-background/95 backdrop-blur-sm">
        <!-- Shimmer overlay -->
        <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-blue-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
      </div>
    </div>
    
    <!-- Main content -->
    <div class="relative bg-background/95 backdrop-blur-sm rounded-xl p-4 border border-border/50 hover:border-border/80 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-blue-500/10">
      <!-- Header with date badge -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-foreground truncate group-hover:text-blue-600 transition-colors duration-300">
            {{ event.title }}
          </h3>
        </div>
        <div class="ml-3 flex-shrink-0">
          <div class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-600 ring-1 ring-blue-500/20">
            <Calendar class="w-3 h-3 mr-1" />
            {{ formatDate(event.time) }}
          </div>
        </div>
      </div>
      
      <!-- Time section with animated icon -->
      <div class="flex items-center mb-3 text-sm text-muted-foreground">
        <div class="flex items-center mr-4 group-hover:text-emerald-600 transition-colors duration-300">
          <Clock class="w-4 h-4 mr-2 group-hover:rotate-12 transition-transform duration-300" />
          {{ event.time }}
        </div>
      </div>
      
      <!-- Location section -->
      <div v-if="event.location" class="flex items-center mb-3 text-sm text-muted-foreground">
        <MapPin class="w-4 h-4 mr-2 text-red-500 group-hover:scale-110 transition-transform duration-300" />
        <span class="truncate">{{ event.location }}</span>
      </div>
      
      <!-- Description -->
      <div v-if="event.description && event.description !== '설명 없음'" 
           class="mb-3 text-sm text-muted-foreground/80 line-clamp-2">
        {{ event.description }}
      </div>
      
      <!-- Attendees section -->
      <div v-if="event.attendees && event.attendees.length > 0" class="flex items-center text-sm text-muted-foreground">
        <Users class="w-4 h-4 mr-2 text-purple-500" />
        <div class="flex -space-x-1">
          <div v-for="(attendee, index) in event.attendees.slice(0, 3)" 
               :key="index" 
               class="w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-blue-600 border-2 border-background flex items-center justify-center text-white text-xs font-bold">
            {{ getInitials(attendee) }}
          </div>
          <div v-if="event.attendees.length > 3" 
               class="w-6 h-6 rounded-full bg-muted border-2 border-background flex items-center justify-center text-xs font-medium">
            +{{ event.attendees.length - 3 }}
          </div>
        </div>
        <span class="ml-2">{{ event.attendees.length }} 참석자</span>
      </div>
      
      <!-- Floating action button -->
      <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button class="w-8 h-8 rounded-full bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 hover:border-blue-500/40 flex items-center justify-center transition-all duration-200 hover:scale-110">
          <ExternalLink class="w-4 h-4 text-blue-600" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Calendar, Clock, MapPin, Users, ExternalLink } from 'lucide-vue-next'

interface CalendarEvent {
  id: string
  title: string
  time: string
  location?: string
  description?: string
  attendees?: string[]
}

interface Props {
  event: CalendarEvent
}

defineProps<Props>()

const formatDate = (timeStr: string) => {
  // Extract date from "07/04 17:00 - 19:00" format
  const dateMatch = timeStr.match(/(\d{2}\/\d{2})/)
  return dateMatch ? dateMatch[1] : ''
}

const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>