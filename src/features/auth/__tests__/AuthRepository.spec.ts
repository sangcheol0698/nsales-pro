// filepath: /Users/sangcheol/IdeaProjects/nsales-pro/frontend/src/features/auth/__tests__/AuthRepository.spec.ts
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthRepository from '@/features/auth/repository/AuthRepository';

// tsyringe 모킹을 import 이전에 선언
vi.mock('tsyringe', () => ({
  singleton: () => (target: any) => target,
  inject: () => () => {
  },
  container: { resolve: vi.fn(() => ({})) },
}));

// zod 스키마 객체 여부를 확인하기 위한 간단한 헬퍼
function isZodSchema(obj: any) {
  return obj && typeof obj.safeParse === 'function';
}

describe('AuthRepository', () => {
  let repo: AuthRepository;
  let http: any;

  beforeEach(() => {
    http = { post: vi.fn(), patch: vi.fn() };
    // @ts-ignore: DI 무시하고 수동 주입
    repo = new AuthRepository(http);
  });

  it('login: 요청에 requestSchema를 포함하고 올바른 경로로 위임', async () => {
    const body = { username: 'user@example.com', password: '12345678' };

    await repo.login(body as any, true);

    expect(http.post).toHaveBeenCalledTimes(1);
    const arg = http.post.mock.calls[0][0];
    expect(arg.path).toBe('/api/v1/auths/login?remember=true');
    expect(arg.body).toEqual(body);
    expect(isZodSchema(arg.requestSchema)).toBe(true);
  });

  it('setPassword: PATCH 위임 확인', async () => {
    const data = { token: 'abc', password: 'newPassword123' };
    await repo.setPassword(data as any);
    expect(http.patch).toHaveBeenCalledWith({ path: '/api/v1/auths/initialize', body: data });
  });
});
