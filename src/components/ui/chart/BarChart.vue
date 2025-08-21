<template>
  <Bar ref="chartRef" :data="data" :options="computedOptions" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Bar } from 'vue-chartjs';
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Title, Tooltip } from 'chart.js';
import { borderVar, foregroundVar, getHslColor, popoverFgVar, popoverVar } from './theme';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

interface Dataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  borderRadius?: number;
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
        labels: { color: fg, usePointStyle: true, pointStyle: 'rectRounded' },
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
    datasets: {
      bar: {
        borderRadius: 6,
        borderSkipped: false as const,
        barPercentage: 0.75,
        categoryPercentage: 0.8,
      },
    },
  };
});

const merge = (a: any, b: any) => ({
  ...a, ...b,
  plugins: { ...(a?.plugins || {}), ...(b?.plugins || {}) },
  scales: { ...(a?.scales || {}), ...(b?.scales || {}) },
  datasets: { ...(a?.datasets || {}), ...(b?.datasets || {}) },
});

// 데이터셋 테마 색상 자동 적용
const themedDatasets = computed(() => {
  const seriesColors = ['--primary', '--secondary', '--ring', '--destructive', '--muted'];
  return props.datasets.map((ds, i) => {
    const colorVar = seriesColors[i % seriesColors.length];
    const bg = Array.isArray(ds.backgroundColor) || ds.backgroundColor
      ? ds.backgroundColor
      : getHslColor(colorVar, 0.8);
    const border = Array.isArray(ds.borderColor) || ds.borderColor
      ? ds.borderColor
      : getHslColor(colorVar);
    return {
      ...ds,
      backgroundColor: bg,
      borderColor: border,
      borderWidth: ds.borderWidth ?? 0,
      borderRadius: ds.borderRadius ?? 6,
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