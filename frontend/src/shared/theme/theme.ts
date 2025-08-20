/**
 * Material-UI theme configuration
 * Implements design system tokens and responsive breakpoints
 */

import { createTheme, ThemeOptions } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// Design tokens
const colors = {
  primary: {
    50: '#e3f2fd',
    100: '#bbdefb',
    200: '#90caf9',
    300: '#64b5f6',
    400: '#42a5f5',
    500: '#2196f3',
    600: '#1e88e5',
    700: '#1976d2',
    800: '#1565c0',
    900: '#0d47a1',
  },
  secondary: {
    50: '#fce4ec',
    100: '#f8bbd9',
    200: '#f48fb1',
    300: '#f06292',
    400: '#ec407a',
    500: '#e91e63',
    600: '#d81b60',
    700: '#c2185b',
    800: '#ad1457',
    900: '#880e4f',
  },
  error: {
    50: '#ffebee',
    100: '#ffcdd2',
    200: '#ef9a9a',
    300: '#e57373',
    400: '#ef5350',
    500: '#f44336',
    600: '#e53935',
    700: '#d32f2f',
    800: '#c62828',
    900: '#b71c1c',
  },
  warning: {
    50: '#fff8e1',
    100: '#ffecb3',
    200: '#ffe082',
    300: '#ffd54f',
    400: '#ffca28',
    500: '#ffc107',
    600: '#ffb300',
    700: '#ffa000',
    800: '#ff8f00',
    900: '#ff6f00',
  },
  success: {
    50: '#e8f5e8',
    100: '#c8e6c9',
    200: '#a5d6a7',
    300: '#81c784',
    400: '#66bb6a',
    500: '#4caf50',
    600: '#43a047',
    700: '#388e3c',
    800: '#2e7d32',
    900: '#1b5e20',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
};

// Typography scale
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 600,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.4,
  },
};

// Spacing scale (8px base unit)
const spacing = 8;

// Breakpoints
const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 960,
    lg: 1280,
    xl: 1920,
  },
};

// Light theme configuration
const lightThemeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary[600],
      light: colors.primary[400],
      dark: colors.primary[800],
      contrastText: '#ffffff',
    },
    secondary: {
      main: colors.secondary[600],
      light: colors.secondary[400],
      dark: colors.secondary[800],
      contrastText: '#ffffff',
    },
    error: {
      main: colors.error[600],
      light: colors.error[400],
      dark: colors.error[800],
      contrastText: '#ffffff',
    },
    warning: {
      main: colors.warning[600],
      light: colors.warning[400],
      dark: colors.warning[800],
      contrastText: '#000000',
    },
    success: {
      main: colors.success[600],
      light: colors.success[400],
      dark: colors.success[800],
      contrastText: '#ffffff',
    },
    grey: colors.grey,
    background: {
      default: colors.grey[50],
      paper: '#ffffff',
    },
    text: {
      primary: colors.grey[900],
      secondary: colors.grey[700],
      disabled: colors.grey[500],
    },
    divider: colors.grey[200],
  },
  typography,
  spacing,
  breakpoints,
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    `0px 1px 3px ${alpha(colors.grey[900], 0.12)}`,
    `0px 1px 5px ${alpha(colors.grey[900], 0.12)}`,
    `0px 1px 8px ${alpha(colors.grey[900], 0.12)}`,
    `0px 1px 10px ${alpha(colors.grey[900], 0.12)}`,
    `0px 1px 14px ${alpha(colors.grey[900], 0.12)}`,
    `0px 1px 18px ${alpha(colors.grey[900], 0.12)}`,
    `0px 2px 16px ${alpha(colors.grey[900], 0.12)}`,
    `0px 3px 14px ${alpha(colors.grey[900], 0.12)}`,
    `0px 3px 16px ${alpha(colors.grey[900], 0.12)}`,
    `0px 4px 18px ${alpha(colors.grey[900], 0.12)}`,
    `0px 4px 20px ${alpha(colors.grey[900], 0.12)}`,
    `0px 5px 22px ${alpha(colors.grey[900], 0.12)}`,
    `0px 5px 24px ${alpha(colors.grey[900], 0.12)}`,
    `0px 5px 26px ${alpha(colors.grey[900], 0.12)}`,
    `0px 6px 28px ${alpha(colors.grey[900], 0.12)}`,
    `0px 6px 30px ${alpha(colors.grey[900], 0.12)}`,
    `0px 6px 32px ${alpha(colors.grey[900], 0.12)}`,
    `0px 7px 34px ${alpha(colors.grey[900], 0.12)}`,
    `0px 7px 36px ${alpha(colors.grey[900], 0.12)}`,
    `0px 8px 38px ${alpha(colors.grey[900], 0.12)}`,
    `0px 8px 40px ${alpha(colors.grey[900], 0.12)}`,
    `0px 8px 42px ${alpha(colors.grey[900], 0.12)}`,
    `0px 9px 44px ${alpha(colors.grey[900], 0.12)}`,
    `0px 9px 46px ${alpha(colors.grey[900], 0.12)}`,
  ],
};

// Dark theme configuration
const darkThemeOptions: ThemeOptions = {
  ...lightThemeOptions,
  palette: {
    mode: 'dark',
    primary: {
      main: colors.primary[400],
      light: colors.primary[300],
      dark: colors.primary[600],
      contrastText: '#000000',
    },
    secondary: {
      main: colors.secondary[400],
      light: colors.secondary[300],
      dark: colors.secondary[600],
      contrastText: '#000000',
    },
    background: {
      default: colors.grey[900],
      paper: colors.grey[800],
    },
    text: {
      primary: colors.grey[100],
      secondary: colors.grey[300],
      disabled: colors.grey[500],
    },
    divider: colors.grey[700],
  },
};

export const lightTheme = createTheme(lightThemeOptions);
export const darkTheme = createTheme(darkThemeOptions);

export { colors, typography, spacing, breakpoints };
