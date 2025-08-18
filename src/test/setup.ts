import { vi } from 'vitest';
import 'reflect-metadata';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock console methods to reduce noise in test output
console.log = vi.fn();
console.error = vi.fn();
console.warn = vi.fn();

// 전역 라우터 모킹: createRouter/createWebHistory 및 훅 제공
vi.mock('vue-router', () => {
  const beforeEach = vi.fn();
  return {
    createRouter: vi.fn(() => ({ beforeEach })),
    createWebHistory: vi.fn(() => ({})),
    RouterView: { name: 'RouterView', setup: () => () => null },
    useRouter: vi.fn(() => ({
      currentRoute: { value: { path: '/' } },
      push: vi.fn(),
      replace: vi.fn(),
    })),
    useRoute: vi.fn(() => ({ path: '/' })),
  };
});

// DI 모킹: tsyringe의 데코레이터와 container
vi.mock('tsyringe', () => {
  const identityClassDecorator = () => (target: any) => target;
  const identityParamDecorator = () => (_target: any, _propertyKey?: string | symbol, _parameterIndex?: number) => {
  };
  return {
    singleton: identityClassDecorator,
    inject: identityParamDecorator,
    container: {
      resolve: vi.fn(() => ({})),
    },
  };
});
