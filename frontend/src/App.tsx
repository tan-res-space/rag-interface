/**
 * Main App component with theme provider, routing, and global providers
 */
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { store } from '@/app/store';
import { lightTheme } from '@shared/theme/theme';
import { AppRoutes } from '@/app/routes';
import { NotificationProvider } from '@shared/components/NotificationProvider';
import { AuthProvider } from '@features/auth/AuthProvider';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={lightTheme}>
          <CssBaseline />
          <NotificationProvider>
            <AuthProvider>
              <AppRoutes />
            </AuthProvider>
          </NotificationProvider>
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
