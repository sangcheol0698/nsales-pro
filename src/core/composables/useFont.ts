import { ref, onMounted, watch } from 'vue';
import { fonts, type FontName } from '@/config/fonts';

export function useFont() {
  // Create a ref to store the current font
  const font = ref<FontName>('Pretendard'); // Default font

  // Function to apply the font to the document
  const applyFont = (fontName: FontName) => {
    console.log('Applying font:', fontName);

    // Special handling for font names with spaces
    const formattedFontName = fontName.includes(' ') ? `'${fontName}'` : fontName;

    const fontFamily = `${formattedFontName}, -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif`;

    console.log('Using font-family:', fontFamily);

    // Apply to documentElement (html)
    document.documentElement.style.setProperty('font-family', fontFamily, 'important');

    // Apply to body
    document.body.style.setProperty('font-family', fontFamily, 'important');

    // Create a style element to apply the font to all elements
    let styleEl = document.getElementById('font-style');
    if (!styleEl) {
      styleEl = document.createElement('style');
      styleEl.id = 'font-style';
      document.head.appendChild(styleEl);
    }

    // Set the style content to apply the font to all elements
    styleEl.textContent = `
      * {
        font-family: ${fontFamily} !important;
      }
    `;

    console.log('Font applied:', fontName);
  };

  // Function to set the font
  const setFont = (newFont: FontName) => {
    console.log('Setting font to:', newFont);

    // Update the ref
    font.value = newFont;

    // Apply the font
    applyFont(newFont);
    console.log('Applied font:', newFont);

    // Save to localStorage
    localStorage.setItem('font', newFont);
    console.log('Saved font to localStorage:', newFont);
  };

  // Initialize font on component mount
  onMounted(() => {
    // Check for saved font in localStorage
    const savedFont = localStorage.getItem('font') as FontName | null;
    console.log('Loaded font from localStorage:', savedFont);

    // Set initial font
    if (savedFont && fonts.includes(savedFont as FontName)) {
      font.value = savedFont as FontName;
      console.log('Setting font to:', font.value);
    } else {
      console.log('Using default font:', font.value);
    }

    // Apply the font
    applyFont(font.value);
    console.log('Applied font:', font.value);
  });

  // Watch for changes in the font ref
  watch(font, (newFont) => {
    console.log('Font changed to:', newFont);
    applyFont(newFont);
    console.log('Applied font from watcher:', newFont);
  });

  return {
    font,
    setFont,
    availableFonts: fonts,
  };
}
