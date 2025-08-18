<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow v-for="headerGroup in tableInstance.getHeaderGroups()" :key="headerGroup.id">
          <TableHead
            v-for="header in headerGroup.headers"
            :key="header.id"
            :class="header.column.id === 'select' ? 'px-2' : ''"
            :style="{ width: getHeaderSizePx(header) + 'px' }"
          >
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()"
            />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <!-- 로딩 상태: 스켈레톤 행 렌더링 -->
        <template v-if="loading">
          <TableRow v-for="i in skeletonRowCount" :key="`skeleton-row-${i}`">
            <TableCell v-for="col in visibleColumns" :key="`skeleton-cell-${i}-${col.id}`"
                       :class="col.id === 'select' ? 'px-2' : ''">
              <template v-if="getColSkeletonVariantByColumn(col) === 'checkbox'">
                <div class="flex items-center">
                  <Skeleton class="h-4 w-4 rounded-sm" />
                </div>
              </template>
              <template v-else-if="getColSkeletonVariantByColumn(col) === 'title-subtitle'">
                <Skeleton class="h-4" :style="{ width: lineWidthPx(col, 0) + 'px' }" />
                <div class="mt-2">
                  <Skeleton class="h-3" :style="{ width: lineWidthPx(col, 1) + 'px' }" />
                </div>
              </template>
              <template v-else>
                <Skeleton class="h-4" :style="{ width: lineWidthPx(col, 0) + 'px' }" />
              </template>
            </TableCell>
          </TableRow>
        </template>

        <!-- 데이터 존재 시 실제 행 렌더링 -->
        <template v-else-if="tableInstance.getRowModel().rows?.length">
          <template v-for="row in tableInstance.getRowModel().rows" :key="row.id">
            <TableRow
              :data-state="row.getIsSelected() && 'selected'"
              class="hover:bg-muted/50"
            >
              <TableCell
                v-for="(cell, idx) in row.getVisibleCells()"
                :key="cell.id"
                :class="[cell.column.id === 'select' ? 'px-2' : '', idx === 1 ? 'pl-2' : '']"
                :style="{ width: getCellSizePx(cell) + 'px' }"
              >
                <FlexRender
                  :render="cell.column.columnDef.cell"
                  :props="cell.getContext()"
                />
              </TableCell>
            </TableRow>

            <!-- Expanded content -->
            <TableRow v-if="row.getIsExpanded() && $slots['expanded-row']" :key="`${row.id}-expanded`">
              <TableCell :colspan="row.getVisibleCells().length">
                <slot name="expanded-row" :row="row" />
              </TableCell>
            </TableRow>
          </template>
        </template>

        <!-- 비어 있음 -->
        <TableRow v-else>
          <TableCell :colspan="columns.length" class="h-24 text-center">
            <div class="flex flex-col items-center justify-center space-y-2">
              <p class="text-muted-foreground">{{ emptyMessage }}</p>
              <p class="text-sm text-muted-foreground">{{ emptyDescription }}</p>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>

<script setup lang="ts">
import type { ColumnDef, Table as TanstackTable } from '@tanstack/vue-table';
import { FlexRender } from '@tanstack/vue-table';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { computed } from 'vue';

interface DataTableProps {
  columns: ColumnDef<any>[];
  data: any[];
  loading?: boolean;
  emptyMessage?: string;
  emptyDescription?: string;
  tableInstance: TanstackTable<any>;
  pageSize?: number; // 현재 페이지 size
}

const props = defineProps<DataTableProps>();


// 가시 컬럼 목록
const visibleColumns = computed(() => props.tableInstance.getVisibleLeafColumns?.() ?? []);

// 스켈레톤 행 수: pageSize가 있으면 그 값 사용, 없으면 8개 기본
const skeletonRowCount = computed(() => (props.pageSize && props.pageSize > 0 ? props.pageSize : 8));

// 컬럼 메타에서 스켈레톤 변형 조회 (컬럼 객체 기반)
function getColSkeletonVariantByColumn(col: any): 'single' | 'title-subtitle' | 'checkbox' {
  if (col?.id === 'select') return 'checkbox';
  const meta = (col?.columnDef as any)?.meta;
  return meta?.skeleton === 'title-subtitle' ? 'title-subtitle' : 'single';
}

// 컬럼의 픽셀 폭 계산 (TanStack Column.getSize 우선, 없으면 columnDef.size, 기본 120)
function getColumnSizePx(col: any): number {
  try {
    if (col?.id === 'select') return 44; // 체크박스 열은 고정 소형 폭
    const size = typeof col?.getSize === 'function' ? col.getSize() : (col?.columnDef?.size ?? 120);
    return Math.max(48, Math.min(400, Number(size) || 120));
  } catch {
    return 120;
  }
}

// 라인별 스켈레톤 너비(px) 계산: 제목/서브는 서로 다른 비율, 작은 컬럼은 더 큰 비율로
function lineWidthPx(col: any, lineIdx = 0): number {
  const base = getColumnSizePx(col);
  const variant = getColSkeletonVariantByColumn(col);
  if (variant === 'checkbox') return 16;

  // 기준 비율
  let primary = 0.72; // 제목줄
  let secondary = 0.45; // 서브줄

  // 컬럼 크기별 비율 세분화
  if (base <= 80) {
    // 작은 컬럼 (체크박스, 상태 등)
    primary = 0.9;
    secondary = 0.6;
  } else if (base <= 160) {
    // 중간 컬럼 (일반 텍스트)
    primary = 0.72;
    secondary = 0.45;
  } else if (base <= 260) {
    // 큰 컬럼 (긴 텍스트)
    primary = 0.65;
    secondary = 0.4;
  } else if (base <= 400) {
    // 매우 큰 컬럼 (프로젝트명, 직원명 등)
    primary = 0.6;
    secondary = 0.35;
  } else {
    // 초대형 컬럼 (500px 프로젝트명 등)
    primary = 0.55;
    secondary = 0.3;
  }

  const ratio = lineIdx === 1 ? secondary : primary;
  // 최소/최대 클램프
  const px = Math.round(base * ratio);
  return Math.max(32, Math.min(px, base - 12));
}

// 헤더/셀 width 계산 유틸
function getHeaderSizePx(header: any): number {
  try {
    const col = header?.column;
    if (col?.id === 'select') return 44;
    const size = typeof col?.getSize === 'function' ? col.getSize() : (col?.columnDef?.size ?? 120);
    return Math.max(48, Math.min(400, Number(size) || 120));
  } catch {
    return 120;
  }
}

function getCellSizePx(cell: any): number {
  try {
    const col = cell?.column;
    if (col?.id === 'select') return 44;
    const size = typeof col?.getSize === 'function' ? col.getSize() : (col?.columnDef?.size ?? 120);
    return Math.max(48, Math.min(400, Number(size) || 120));
  } catch {
    return 120;
  }
}
</script>