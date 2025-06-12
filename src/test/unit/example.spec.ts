import { describe, it, expect } from 'vitest';

describe('예제 테스트', () => {
  it('통과해야 함', () => {
    expect(true).toBe(true);
  });

  it('기본 수학 연산을 처리해야 함', () => {
    expect(1 + 1).toBe(2);
    expect(2 * 2).toBe(4);
  });
});
