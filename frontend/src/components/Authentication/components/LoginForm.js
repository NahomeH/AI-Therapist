// components/Authentication/LoginForm.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { useAuthForm } from '../hooks/useAuthForm';
import FormField from './FormField';

function LoginForm({ onSwitchToSignup }) {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  
  const form = useAuthForm(true, {
    onSignInSuccess: () => navigate('/chat'),
    signIn
  });
  
  return (
    <>
      <form onSubmit={form.handleSubmit} className="auth-form">
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
          {form.isSubmitting ? 'Loading...' : 'Log In'}
        </button>
      </form>
      <button 
        className="auth-toggle-btn"
        onClick={onSwitchToSignup}
      >
        Don't have an account? Sign up
      </button>
    </>
  );
}

export default LoginForm;