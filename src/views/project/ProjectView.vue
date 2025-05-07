<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>프로젝트</TableHead>
            <TableHead>유형</TableHead>
            <TableHead>기간</TableHead>
            <TableHead>계약일</TableHead>
            <TableHead>계약금액</TableHead>
            <TableHead>주관사</TableHead>
            <TableHead>고객사</TableHead>
            <TableHead>상태</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="data.length > 0">
            <TableRow v-for="project in data" :key="project.id">
              <TableCell>
                <div class="flex flex-col">
                  <span class="font-medium">{{ project.name || '-' }}</span>
                  <span class="text-xs text-muted-foreground">{{ project.code || '' }}</span>
                </div>
              </TableCell>
              <TableCell>{{ project.type || '-' }}</TableCell>
              <TableCell
                >{{
                  (project.startDate || '-') +
                  (project.startDate && project.endDate ? ' ~ ' : '') +
                  (project.endDate || '')
                }}
              </TableCell>
              <TableCell>{{ project.contractDate || '-' }}</TableCell>
              <TableCell>{{ project.contractAmount ? project.contractAmount.toLocaleString() + '원' : '-' }}
              </TableCell>
              <TableCell>{{ project.mainCompany || '-' }}</TableCell>
              <TableCell>{{ project.clientCompany || '-' }}</TableCell>
              <TableCell>{{ project.status || '-' }}</TableCell>
            </TableRow>
          </template>
          <template v-else>
            <TableEmpty :colspan="8">
              <div class="flex flex-col items-center">
                <p class="text-lg font-medium">프로젝트가 없습니다</p>
                <p class="text-sm text-muted-foreground">
                  새 프로젝트를 추가하거나 검색 조건을 변경해보세요
                </p>
              </div>
            </TableEmpty>
          </template>
        </TableBody>
      </Table>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { SidebarLayout } from '@/components/sidebar';
import { onMounted, ref } from 'vue';
import { container } from 'tsyringe';
import ProjectRepository from '@/repository/ProjectRepository.ts';
import type { ProjectSearch } from '@/enity/project/ProjectSearch.ts';
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils.ts';

const params = ref({
  page: 1,
  limit: 10,
});

let PROJECT_REPOSITORY = container.resolve(ProjectRepository);

const data = ref<ProjectSearch[]>([]);

onMounted(() => {
  PROJECT_REPOSITORY.getProjects(params.value)
    .then((projects) => {
      data.value = projects.content;
      console.log(data.value);
    })
    .catch((error) => {
      console.error(error);
    });
});
</script>

<style scoped></style>
