/**
 * Main App component with theme provider, routing, and global providers
 *
 * Documentation:
 * - Frontend Architecture: docs/frontend/UI_UX_Architecture_Design.md
 * - Error Reporting UI: docs/frontend/ErrorReporting_Complete_Design_Documentation.md
 * - User Experience Workflows: docs/frontend/User_Experience_Workflows_Design.md
 * - Development Guide: docs/development/DEVELOPMENT_GUIDE.md
 */
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { store } from '@/app/store';
import { lightTheme } from '@shared/theme/theme';
import { AppRoutes } from '@/app/routes';
import { NotificationProvider } from '@shared/components/NotificationProvider';
import { AuthProvider } from '@features/auth/AuthProvider';
import ErrorBoundary from '@shared/components/ErrorBoundary';
import ErrorProvider from '@shared/components/ErrorProvider';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={lightTheme}>
          <CssBaseline />
          <ErrorBoundary>
            <ErrorProvider>
              <NotificationProvider>
                <AuthProvider>
                  <AppRoutes />
                </AuthProvider>
              </NotificationProvider>
            </ErrorProvider>
          </ErrorBoundary>
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
