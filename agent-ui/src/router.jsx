import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from './App';
import { useAuth } from './contexts/AuthContext';

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mb-4 mx-auto animate-pulse">
            <span className="text-2xl text-white font-bold">M</span>
          </div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Will show AuthModal in App.jsx
    return children;
  }

  return children;
}

// OAuth Callback Handler
function OAuthCallback() {
  const { loading } = useAuth();

  // This component handles the redirect from Google OAuth
  // Token is extracted from URL and stored in AuthContext
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mb-4 mx-auto animate-pulse">
            <span className="text-2xl text-white font-bold">M</span>
          </div>
          <p className="text-gray-400">Completing sign in...</p>
        </div>
      </div>
    );
  }

  // After loading, redirect to home
  return <Navigate to="/" replace />;
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <App />
      </ProtectedRoute>
    ),
  },
  {
    path: '/oauth/callback',
    element: <OAuthCallback />,
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);