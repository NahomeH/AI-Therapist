import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/Authentication/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import ChatInterface from './components/Chatbot/ChatInterface'; 
import AuthContainer from './components/Authentication/AuthContainer';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/auth" element={<AuthContainer />} />
          <Route path="/chat" element=
            {
              <ProtectedRoute>
                <ChatInterface />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/auth" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;