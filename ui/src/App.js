import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';

// Layout components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';

// Page components
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import SettingsPage from './pages/SettingsPage';
import AgentsPage from './pages/AgentsPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';

// Context
import { ApiProvider } from './contexts/ApiContext';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeContext } from './contexts/ThemeContext';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// App component
function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false;
  });

  // Create theme based on dark mode preference
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#2196f3',
      },
      secondary: {
        main: '#f50057',
      },
    },
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
    },
  });

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('darkMode', JSON.stringify(!darkMode));
  };

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <ApiProvider>
            <AuthProvider>
              <Router>
                <div className="app">
                  <Header />
                  <div className="main-container">
                    <Sidebar />
                    <main className="content">
                      <Routes>
                        <Route path="/" element={<DashboardPage />} />
                        <Route path="/chat" element={<ChatPage />} />
                        <Route path="/documents" element={<DocumentsPage />} />
                        <Route path="/agents" element={<AgentsPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                        <Route path="*" element={<NotFoundPage />} />
                      </Routes>
                    </main>
                  </div>
                  <Footer />
                </div>
              </Router>
            </AuthProvider>
          </ApiProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}

export default App;
