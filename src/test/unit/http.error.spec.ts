// filepath: /Users/sangcheol/IdeaProjects/nsales-pro/frontend/src/test/unit/http.error.spec.ts
import { describe, expect, it } from 'vitest';
import HttpError from '@/core/http/HttpError';

// AxiosError 최소 형태 모형
function makeAxiosError(status: number, data: any) {
  return {
    response: {
      status,
      data,
      statusText: 'Bad Request',
    },
  } as any;
}

describe('HttpError mapping', () => {
  it('400 Bad Request는 서버의 message를 그대로 사용한다', () => {
    const server = {
      code: '400',
      status: 'Bad Request',
      message: '이미 존재하는 이메일 입니다.',
      path: '/api/v1/employees',
      timestamp: '2025-08-18T22:06:14.711774',
      validation: {},
    };
    const err = new HttpError(makeAxiosError(400, server));
    expect(err.getCode()).toBe('400');
    expect(err.getMessage()).toBe('이미 존재하는 이메일 입니다.');
  });

  it('401은 세션 만료 고정 메시지로 변환한다', () => {
    const err = new HttpError(makeAxiosError(401, { message: 'ignored' }));
    expect(err.getCode()).toBe('401');
    expect(err.getMessage()).toContain('세션');
  });

  it('기타 상태코드는 서버 message/detail 없으면 기본 메시지', () => {
    const err = new HttpError(makeAxiosError(500, {}));
    expect(err.getCode()).toBe('500');
    expect(err.getMessage()).toBe('서버와의 연결이 원활하지 않습니다.');
  });
});

