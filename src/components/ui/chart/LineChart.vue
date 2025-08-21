<template>
  <Line ref="chartRef" :data="data" :options="computedOptions" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Line } from 'vue-chartjs';
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { borderVar, foregroundVar, getHslColor, popoverFgVar, popoverVar } from './theme';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

interface Dataset {
  label: string;
  data: number[];
  borderColor?: string;
  backgroundColor?: string;
  tension?: number;
  fill?: boolean;
}

const props = withDefaults(defineProps<{
  labels: string[]
  datasets: Dataset[]
  options?: any
}>(), {
  options: () => ({}),
});

const chartRef = ref<any>(null);

// 기본 테마 옵션
const baseOptions = computed(() => {
  const fg = getHslColor(foregroundVar);
  const grid = getHslColor(borderVar, 0.3);
  const tooltipBg = getHslColor(popoverVar);
  const tooltipFg = getHslColor(popoverFgVar);

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { intersect: false, mode: 'index' as const },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: { color: fg, usePointStyle: true, pointStyle: 'line' },
      },
      tooltip: {
        enabled: true,
        backgroundColor: tooltipBg,
        titleColor: tooltipFg,
        bodyColor: tooltipFg,
        borderColor: grid,
        borderWidth: 1,
        padding: 10,
        displayColors: true,
      },
      title: { display: false },
    },
    scales: {
      x: {
        grid: { color: grid, drawBorder: false },
        ticks: { color: fg },
      },
      y: {
        beginAtZero: true,
        grid: { color: grid, drawBorder: false },
        ticks: { color: fg },
      },
    },
    elements: {
      point: {
        radius: 2,
        hoverRadius: 4,
        hitRadius: 8,
        backgroundColor: getHslColor('--primary'),
        borderWidth: 0,
      },
      line: {
        borderWidth: 2,
        tension: 0.35,
      },
    },
  };
});

// 간단 병합 유틸(깊은 병합이 필요할 정도는 아님)
const merge = (a: any, b: any) => ({
  ...a, ...b,
  plugins: { ...(a?.plugins || {}), ...(b?.plugins || {}) },
  scales: { ...(a?.scales || {}), ...(b?.scales || {}) },
  elements: { ...(a?.elements || {}), ...(b?.elements || {}) },
});

// 데이터셋 테마 색상 자동 적용
const themedDatasets = computed(() => {
  const seriesColors = ['--primary', '--secondary', '--ring', '--destructive', '--muted'];
  return props.datasets.map((ds, i) => {
    const colorVar = seriesColors[i % seriesColors.length];
    const border = ds.borderColor || getHslColor(colorVar);
    const bg = ds.backgroundColor || getHslColor(colorVar, 0.18);
    return {
      ...ds,
      borderColor: border,
      backgroundColor: ds.fill === false ? undefined : bg,
      fill: ds.fill ?? true,
      tension: ds.tension ?? 0.35,
    };
  });
});

const data = computed(() => ({
  labels: props.labels,
  datasets: themedDatasets.value,
}));

const computedOptions = computed(() => merge(baseOptions.value, props.options));
</script>

<style scoped>
:host {
  display: block;
}
</style>