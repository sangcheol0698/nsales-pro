<template>
  <MyPageLayout>
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">활동 내역</h3>
        <p class="text-sm text-muted-foreground">최근 계정 활동 내역을 확인합니다.</p>
      </div>
      <div class="space-y-4">
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchActivities"
          searchPlaceholder="활동 검색..."
          searchColumnId="activity"
          :getColumnLabel="getColumnLabel"
          emptyMessage="활동 내역이 없습니다"
          emptyDescription="활동 내역이 생성되면 여기에 표시됩니다"
        />
        <p class="text-xs text-muted-foreground">
          이 기능은 현재 개발 중이며, 샘플 데이터만 표시됩니다.
        </p>
      </div>
    </div>
  </MyPageLayout>
</template>

<script setup lang="ts">
import { h } from 'vue';
import type { ColumnDef } from '@tanstack/vue-table';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';
import { DataTableWithUrl } from '@/shared/components/table';
import { DataTableColumnHeader } from '@/core/components/ui/data-table';
import PageResponse from '@/core/common/PageResponse';

// 활동 내역 인터페이스
interface ActivityRecord {
  id: string;
  activity: string;
  date: string;
  ipAddress: string;
}

// 샘플 데이터
const sampleData: ActivityRecord[] = [
  {
    id: '1',
    activity: '로그인',
    date: '2023-06-01 09:30:45',
    ipAddress: '192.168.1.1'
  },
  {
    id: '2',
    activity: '비밀번호 변경',
    date: '2023-05-15 14:22:10',
    ipAddress: '192.168.1.1'
  },
  {
    id: '3',
    activity: '프로필 업데이트',
    date: '2023-05-10 11:15:22',
    ipAddress: '192.168.1.1'
  },
  {
    id: '4',
    activity: '로그인',
    date: '2023-04-28 16:45:30',
    ipAddress: '192.168.1.1'
  }
];

// 컬럼 정의
const columns: ColumnDef<ActivityRecord>[] = [
  {
    accessorKey: 'activity',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '활동' }),
    cell: ({ row }) => h('div', {}, row.getValue('activity')),
  },
  {
    accessorKey: 'date',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '날짜' }),
    cell: ({ row }) => h('div', {}, row.getValue('date')),
  },
  {
    accessorKey: 'ipAddress',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'IP 주소' }),
    cell: ({ row }) => h('div', {}, row.getValue('ipAddress')),
  }
];

// 컬럼 라벨 가져오기
function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'activity': return '활동';
    case 'date': return '날짜';
    case 'ipAddress': return 'IP 주소';
    default: return columnId;
  }
}

// 데이터 가져오기 (실제로는 API 호출)
async function fetchActivities(params: Record<string, any>): Promise<PageResponse<ActivityRecord>> {
  console.log('Fetching activities with params:', params);

  // 실제 구현에서는 API 호출로 대체
  return new Promise((resolve) => {
    setTimeout(() => {
      // 필터링 처리
      let filteredData = [...sampleData];

      // 활동명으로 필터링
      if (params.activity) {
        const searchTerm = params.activity.toLowerCase();
        filteredData = filteredData.filter(item => 
          item.activity.toLowerCase().includes(searchTerm)
        );
      }

      // 정렬 처리
      if (params.sort && params.direction) {
        const sortField = params.sort as keyof ActivityRecord;
        const sortDirection = params.direction;

        filteredData.sort((a, b) => {
          const valueA = a[sortField];
          const valueB = b[sortField];

          if (sortDirection === 'asc') {
            return valueA > valueB ? 1 : -1;
          } else {
            return valueA < valueB ? 1 : -1;
          }
        });
      }

      // 페이지네이션 처리
      const page = params.page || 1;
      const limit = params.limit || 10;
      const start = (page - 1) * limit;
      const end = start + limit;
      const paginatedData = filteredData.slice(start, end);

      // PageResponse 객체 생성
      const response = new PageResponse<ActivityRecord>({
        content: paginatedData,
        page: page,
        size: limit,
        totalElements: filteredData.length,
        totalPages: Math.ceil(filteredData.length / limit)
      });

      console.log('Activities loaded:', response);
      resolve(response);
    }, 500); // 로딩 시뮬레이션
  });
}
</script>

<style scoped></style>
