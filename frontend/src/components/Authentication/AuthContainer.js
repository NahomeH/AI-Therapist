// components/Authentication/AuthContainer.js
import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import SignupSuccess from './components/SignupSuccess';
import './AuthContainer.css';

function AuthContainer() {
  const [currentView, setCurrentView] = useState('login');
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const handleViewChange = (newView) => {
    setIsTransitioning(true);
    
    setTimeout(() => {
      setCurrentView(newView);
      setIsTransitioning(false);
    }, 200); // Matches the CSS transition duration
  };
  
  // Render content based on current view
  const renderContent = () => {
    switch(currentView) {
      case 'login':
        return <LoginForm onSwitchToSignup={() => handleViewChange('signup')} />;
      case 'signup':
        return (
          <SignupForm 
            onSwitchToLogin={() => handleViewChange('login')}
            onSignupSuccess={() => handleViewChange('success')}
          />
        );
      case 'success':
        return <SignupSuccess onLoginClick={() => handleViewChange('login')} />;
      default:
        return null;
    }
  };
  
  // Determine the title based on current view
  const getTitle = () => {
    switch(currentView) {
      case 'login':
        return 'Welcome Back';
      case 'signup':
        return 'Begin Your Journey';
      case 'success':
        return 'Welcome to Talk2Me';
      default:
        return '';
    }
  };
  
  return (
    <div className="app-container">
      <div className={`auth-window ${isTransitioning ? "transitioning" : ""}`}>
        <h2 className="auth-title">{getTitle()}</h2>
        <div className="auth-form-container">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default AuthContainer;