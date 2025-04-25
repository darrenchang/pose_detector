import type { GlobalThemeOverrides } from 'naive-ui';

// Typography
export const typographyPrimaryTextColor = '#fff';

// Theme (default)
export const defaultTheme:GlobalThemeOverrides = {
  common: {
    primaryColor: '#95F9FF',
    primaryColorHover: typographyPrimaryTextColor,
    primaryColorPressed: typographyPrimaryTextColor,
  },
  Layout: {
    color: '#2A2A2E',
  },
};
