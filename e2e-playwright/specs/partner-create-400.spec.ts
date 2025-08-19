import { expect, test } from '@playwright/test';

// 서버가 400을 줄 때 토스트에 서버 메시지가 그대로 노출되는지 검증
// 전제: 라우터 가드가 localStorage.user 유무를 확인하므로, 네비게이션 전에 user를 주입함

test.describe('Partner Create - 400 Server Message Toast', () => {
  test.beforeEach(async ({ page }) => {
    // 로그인 우회용 사용자 정보 주입 (네비게이션 전에 실행)
    await page.addInitScript(() => {
      localStorage.setItem('user', JSON.stringify({ id: 1, name: '테스터', email: 'tester@example.com' }));
    });

    // 필수 API 스텁: 목록/통계/필터용 전체 조회 등을 최소 응답으로 반환
    await page.route('**/api/v1/partners/stats', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ totalPartners: 0, activePartners: 0, averageGrade: 'C', revenueContribution: 0 }),
      });
    });

    await page.route('**/api/v1/partners?**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ page: 1, size: 10, totalPages: 0, totalElements: 0, content: [] }),
      });
    });

    // 필터용 전체 데이터 로딩(size=1000, page=0)
    await page.route('**/api/v1/partners', async (route, request) => {
      const url = new URL(request.url());
      if (request.method() === 'GET' && url.searchParams.get('size') === '1000') {
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ content: [] }) });
      }
      return route.fallback();
    });
  });

  test('shows server message on 400 when creating partner', async ({ page }) => {
    // 파트너 생성 400 스텁
    await page.route('**/api/v1/partners', async (route, request) => {
      if (request.method() === 'POST') {
        return route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            code: '400',
            status: 'Bad Request',
            message: '이미 존재하는 이메일 입니다.',
            path: '/api/v1/partners',
            timestamp: '2025-08-18T22:06:14.711774',
            validation: {},
          }),
        });
      }
      return route.fallback();
    });

    // 파트너 목록 진입
    await page.goto('/partners');

    // 초기 로딩 완료 대기: 통계/목록/필터 호출이 끝날 때까지
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/v1/partners/stats') && res.status() === 200),
      page.waitForResponse((res) => res.url().includes('/api/v1/partners?') && res.status() === 200),
      page.waitForLoadState('networkidle'),
    ]);

    // 협력사 추가 다이얼로그 열기 (데스크톱 버튼 시도 -> 실패 시 모바일 드롭다운 폴백)
    const desktopBtn = page.getByTestId('add-partner-btn');
    const desktopVisible = await desktopBtn.isVisible().catch(() => false);
    if (desktopVisible) {
      await desktopBtn.click();
    } else {
      // 모바일 뷰포트로 전환 후 액션 메뉴 오픈
      await page.setViewportSize({ width: 375, height: 800 });
      await page.getByRole('button', { name: '액션 메뉴' }).click();
      await page.getByRole('menuitem', { name: /협력사 추가/ }).click();
    }

    // 다이얼로그가 열린 것을 확인
    await expect(page.getByRole('heading', { name: '협력사 추가' })).toBeVisible();

    // 필수 입력값 채우기 (placeholder 기반)
    await page.getByPlaceholder('협력사명을 입력하세요').fill('중복협력사');
    await page.getByPlaceholder('대표자명을 입력하세요').fill('홍길동');
    await page.getByPlaceholder('영업대표명을 입력하세요').fill('김영업');
    await page.getByPlaceholder('010-0000-0000').fill('010-1111-2222');

    // 제출
    await page.getByRole('button', { name: /협력사 생성/ }).click();

    // 토스트: 제목과 서버 메시지(설명) 모두 노출되는지 확인
    await expect(page.getByText('협력사 생성 실패')).toBeVisible();
    await expect(page.getByText('이미 존재하는 이메일 입니다.')).toBeVisible();
  });
});
