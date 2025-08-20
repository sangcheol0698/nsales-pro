// Theme helpers for Chart.js to align with shadcn/ui design tokens

export const cssVar = (name: string) => `var(${name})`;

// Returns raw value of the CSS variable (e.g., "221.2 83.2% 53.3%")
export const getVarValue = (name: string): string => {
  if (typeof window === 'undefined') return '';
  const root = document.documentElement;
  return getComputedStyle(root).getPropertyValue(name).trim();
};

// Returns a valid hsl(...) string resolved from CSS variable (e.g., hsl(221.2 83.2% 53.3% / 0.15))
export const getHslColor = (name: string, alpha?: number) => {
  const v = getVarValue(name);
  if (!v) return alpha != null ? `hsl(0 0% 0% / ${alpha})` : 'hsl(0 0% 0%)';
  return `hsl(${v}${alpha != null ? ` / ${alpha}` : ''})`;
};

// Deprecated for canvas usage; kept for compatibility where CSS vars are supported directly in DOM
export const hslVar = (name: string, alpha?: number) => {
  return `hsl(${cssVar(name)}${alpha != null ? ` / ${alpha}` : ''})`;
};

export const paletteVars = [
  '--primary',
  '--secondary',
  '--muted',
  '--destructive',
  '--ring',
] as const;

export const foregroundVar = '--muted-foreground';
export const borderVar = '--border';
export const backgroundVar = '--background';
export const popoverVar = '--popover';
export const popoverFgVar = '--popover-foreground';

export const compactNumber = (value: number, currency?: 'KRW' | 'USD' | 'JPY') => {
  try {
    if (currency) {
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency,
        notation: 'compact',
        maximumFractionDigits: 1,
      }).format(value);
    }
    return new Intl.NumberFormat('ko-KR', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  } catch {
    return String(value);
  }
};