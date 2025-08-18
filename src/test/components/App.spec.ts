import { describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import App from '@/App.vue';

// vue-router 모킹을 import 이전에 선언
vi.mock('vue-router', () => ({
  RouterView: {
    name: 'RouterView',
    setup: () => () => 'RouterView (mocked)',
  },
  createRouter: vi.fn(() => ({ beforeEach: vi.fn() })),
  createWebHistory: vi.fn(() => ({})),
}));

describe('App.vue', () => {
  it('올바르게 렌더링되는지 확인', () => {
    const wrapper = mount(App);
    expect(wrapper.exists()).toBe(true);
    // RouterView 스텁이 렌더링되었는지만 확인
    expect(wrapper.text()).toContain('RouterView (mocked)');
  });
});
