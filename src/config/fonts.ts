// Available fonts for the application
export const fonts = [
  'Pretendard',
  'D2Coding',
  'IBM Plex Mono',
  'Roboto Mono',
  'Courier New'
] as const;

// Type for font names
export type FontName = typeof fonts[number];
