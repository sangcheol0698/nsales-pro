import { describe, it, expect } from 'vitest';

describe('Example Test', () => {
  it('should pass', () => {
    expect(true).toBe(true);
  });

  it('should handle basic math', () => {
    expect(1 + 1).toBe(2);
    expect(2 * 2).toBe(4);
  });
});