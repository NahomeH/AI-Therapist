// Main form component (UI & form logic orchestration)

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Smile, Calendar, Mail, Lock } from 'lucide-react';
import { useAuth } from './AuthContext';
import { useAuthForm } from './hooks/useAuthForm';
import FormField from './components/FormField';
import SignupSuccess from './components/SignupSuccess';
import './AuthenticationForm.css';

function AuthenticationForm() {
  const navigate = useNavigate();
  const { signIn, signUp, user } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [signupSuccess, setSignupSuccess] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const form = useAuthForm(isLogin, {
    onSignInSuccess: () => navigate('/chat'),
    onSignUpSuccess: () => setSignupSuccess(true),
    signIn,
    signUp
  });

  useEffect(() => {
    if (user) {
      navigate('/chat');
    }
  }, [user, navigate]);

  const handleToggleMode = () => {
    setIsTransitioning(true); // Start fade-out
  
    setTimeout(() => {
      setIsLogin((prev) => !prev); // Switch login mode
      form.reset(); // Reset form after switching
      setIsTransitioning(false); // Start fade-in
    }, 200); // Delay to match CSS transition duration
  };

  if (signupSuccess) {
    return (
      <SignupSuccess 
        onLoginClick={() => {
          setIsLogin(true);
          setSignupSuccess(false);
          form.reset();
        }}
      />
    );
  }

  return (
    <div className="app-container">
      <div className={`auth-window ${isTransitioning ? "transitioning" : ""}`}>
        <h2 className="auth-title">
          {isLogin ? 'Welcome Back' : 'Begin Your Journey'}
        </h2>
        <div className="auth-form-container">
          <form onSubmit={form.handleSubmit} className="auth-form">
            {!isLogin && (
              <>
                <FormField
                  icon={User}
                  placeholder="Enter your full name"
                  error={form.errors.fullName}
                  registration={form.register('fullName')}
                />
                <FormField
                  icon={Smile}
                  placeholder="What should we call you?"
                  registration={form.register('preferredName')}
                />
              </>
            )}
            
            <FormField
              icon={Mail}
              type="email"
              placeholder="Enter your email"
              error={form.errors.email}
              registration={form.register('email')}
            />

            <FormField
              icon={Lock}
              type="password"
              placeholder="Enter your password"
              error={form.errors.password}
              registration={form.register('password')}
            />

            {!isLogin && (
              <>
                <FormField
                  icon={Lock}
                  type="password"
                  placeholder="Confirm your password"
                  error={form.errors.confirmPassword}
                  registration={form.register('confirmPassword')}
                />
                <FormField
                  icon={Calendar}
                  type="date"
                  error={form.errors.dateOfBirth}
                  registration={form.register('dateOfBirth')}
                  max={new Date().toISOString().split('T')[0]}
                />
              </>
            )}

            {form.error && (
              <div className="auth-error">
                {form.error}
              </div>
            )}

            <button 
              type="submit" 
              className="submit-btn"
              disabled={form.isSubmitting}
            >
              {form.isSubmitting 
                ? 'Loading...' 
                : (isLogin ? 'Log In' : 'Sign Up')
              }
            </button>
          </form>
        </div>
        <button 
          className="auth-toggle-btn"
          onClick={handleToggleMode}
        >
          {isLogin 
            ? "Don't have an account? Sign up" 
            : "Already have an account? Log in"}
        </button>
      </div>
    </div>
  );
}

export default AuthenticationForm;