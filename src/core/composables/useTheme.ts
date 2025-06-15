import { ref, onMounted, computed } from 'vue';

// Define the available themes
export type Theme = 'light' | 'dark';

export function useTheme() {
  // Create a ref to store the current theme
  const storedTheme = ref<Theme>('light');

  // Computed property for the effective theme (same as storedTheme in this case)
  const effectiveTheme = computed<'light' | 'dark'>(() => {
    return storedTheme.value;
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

  // Function to toggle between light and dark
  const toggleTheme = () => {
    // Toggle between light and dark
    setTheme(storedTheme.value === 'light' ? 'dark' : 'light');
  };

  // Initialize theme on component mount
  onMounted(() => {
    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme') as Theme | null;

    // Set initial theme
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      storedTheme.value = savedTheme;
    }

    // Apply the effective theme
    applyTheme(effectiveTheme.value === 'dark');
  });

  return {
    theme: storedTheme,
    effectiveTheme,
    setTheme,
    toggleTheme,
  };
}
