// Available fonts for the application
export const fonts = [
  'Pretendard',
  'Arial',
  'Helvetica',
  'Times New Roman',
  'Courier New',
  'Verdana',
  'Georgia',
  'Palatino',
  'Garamond',
  'Bookman',
  'Tahoma',
  'Trebuchet MS'
] as const;

// Type for font names
export type FontName = typeof fonts[number];