// App.js
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/Authentication/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import Layout from './Layout';
import ChatInterface from './components/Chatbot/ChatInterface'; 
import AuthContainer from './components/Authentication/AuthContainer';
import Appointments from './components/Appointments/Appointments';
import AgentPreferences from './components/AgentPreferences/AgentPreferences';
import Dashboard from './components/Dashboard/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Auth route (outside layout) */}
          <Route path="/auth" element={<AuthContainer />} />
          
          {/* Layout wrapper for authenticated routes */}
          <Route element={<ProtectedRoute> <Layout /> </ProtectedRoute>}>
            <Route path="/dashboard" element={
                <Dashboard />
            } />
            
            <Route path="/chat" element={
                <ChatInterface />
            } />

            <Route path="/appointments" element={
                <Appointments />
            } />
            
            <Route path="/preferences" element={
                <AgentPreferences />
            } />
            
            {/* Add other routes as needed */}
            {/* <Route path="/history" element={
              <ProtectedRoute>
                <SessionHistory />
              </ProtectedRoute>
            } /> */}
            
            {/* <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } /> */}
          </Route>
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/auth" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;