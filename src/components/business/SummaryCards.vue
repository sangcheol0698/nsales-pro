<template>
  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
    <SummaryCard
      v-for="card in cards"
      :key="card.title"
      v-bind="card"
    />
  </div>
</template>

<script setup lang="ts">
import { type LucideIcon } from 'lucide-vue-next';
import SummaryCard from './SummaryCard.vue';

interface SummaryCardData {
  title: string;
  value: number | string;
  previousValue?: number;
  description?: string;
  icon: LucideIcon;
  formatType?: 'number' | 'currency' | 'percentage' | 'text';
  showTrend?: boolean;
}

interface SummaryCardsProps {
  cards: SummaryCardData[];
}

defineProps<SummaryCardsProps>();
</script>