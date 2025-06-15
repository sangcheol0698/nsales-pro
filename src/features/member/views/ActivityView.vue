<template>
  <MyPageLayout :loading="loading">
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">활동 내역</h3>
        <p class="text-sm text-muted-foreground">최근 계정 활동 내역을 확인합니다.</p>
      </div>
      <div class="space-y-4">
        <div class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>활동</TableHead>
                <TableHead>날짜</TableHead>
                <TableHead>IP 주소</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>로그인</TableCell>
                <TableCell>2023-06-01 09:30:45</TableCell>
                <TableCell>192.168.1.1</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>비밀번호 변경</TableCell>
                <TableCell>2023-05-15 14:22:10</TableCell>
                <TableCell>192.168.1.1</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <p class="text-xs text-muted-foreground">
          이 기능은 현재 개발 중이며, 샘플 데이터만 표시됩니다.
        </p>
      </div>
    </div>
  </MyPageLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';

const loading = ref(false);
</script>

<style scoped></style>
