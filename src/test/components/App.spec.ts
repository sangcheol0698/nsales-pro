import { describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import App from '@/App.vue';

// RouterView 컴포넌트 모킹
vi.mock('vue-router', () => ({
  RouterView: {
    name: 'RouterView',
    setup: () => () => 'RouterView (mocked)',
  },
}));

describe('App.vue', () => {
  it('올바르게 렌더링되는지 확인', () => {
    const wrapper = mount(App);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('div').exists()).toBe(true);
    // 실제 구현에서 div에는 클래스가 없음
    expect(wrapper.find('div').classes()).toEqual([]);
  });
});
