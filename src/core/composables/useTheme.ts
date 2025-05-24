import { ref, onMounted, computed } from 'vue';

// Define the available themes
export type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
  // Create a ref to store the current theme
  const storedTheme = ref<Theme>('system');

  // Track system preference separately
  const systemPrefersDark = ref(false);

  // Computed property for the effective theme
  const effectiveTheme = computed<'light' | 'dark'>(() => {
    if (storedTheme.value === 'system') {
      return systemPrefersDark.value ? 'dark' : 'light';
    }
    return storedTheme.value as 'light' | 'dark';
  });

  // Function to apply the theme to the document
  const applyTheme = (isDark: boolean) => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Function to set the theme
  const setTheme = (newTheme: Theme) => {
    // Update the ref
    storedTheme.value = newTheme;

    // Apply the effective theme
    applyTheme(effectiveTheme.value === 'dark');

    // Save to localStorage
    localStorage.setItem('theme', newTheme);
  };

  // Function to toggle between light and dark (not system)
  const toggleTheme = () => {
    // If current theme is system, switch to the opposite of system preference
    if (storedTheme.value === 'system') {
      setTheme(systemPrefersDark.value ? 'light' : 'dark');
    } else {
      // Otherwise toggle between light and dark
      setTheme(storedTheme.value === 'light' ? 'dark' : 'light');
    }
  };

  // Function to update system preference
  const updateSystemPreference = () => {
    systemPrefersDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // If theme is set to system, apply the system preference
    if (storedTheme.value === 'system') {
      applyTheme(systemPrefersDark.value);
    }
  };

  // Initialize theme on component mount
  onMounted(() => {
    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme') as Theme | null;

    // Update system preference
    updateSystemPreference();

    // Set initial theme
    if (savedTheme) {
      storedTheme.value = savedTheme;
    }

    // Apply the effective theme
    applyTheme(effectiveTheme.value === 'dark');

    // Watch for changes in system preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      updateSystemPreference();
    };

    // Add event listener
    mediaQuery.addEventListener('change', handleChange);

    // Clean up
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  });

  return {
    theme: storedTheme,
    effectiveTheme,
    setTheme,
    toggleTheme,
  };
}
