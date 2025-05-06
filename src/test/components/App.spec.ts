import { describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import App from '@/App.vue';

// Mock the RouterView component
vi.mock('vue-router', () => ({
  RouterView: {
    name: 'RouterView',
    setup: () => () => 'RouterView (mocked)',
  },
}));

describe('App.vue', () => {
  it('renders properly', () => {
    const wrapper = mount(App);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('div').exists()).toBe(true);
    expect(wrapper.find('div').classes()).toContain('min-h-screen');
    expect(wrapper.find('div').classes()).toContain('w-full');
  });
});
