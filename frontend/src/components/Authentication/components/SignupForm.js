// components/Authentication/components/SignupForm.js
import React from 'react';
import { User, Smile, Calendar, Mail, Lock} from 'lucide-react';
import { useAuth } from '../AuthContext';
import { useAuthForm } from '../hooks/useAuthForm';
import FormField from './FormField';
import LegalCheckbox from './LegalCheckbox';

function SignupForm({ onSwitchToLogin, onSignupSuccess }) {
  const { signUp } = useAuth();
  
  const form = useAuthForm(false, {
    onSignUpSuccess: onSignupSuccess,
    signUp
  });
  
  return (
    <>
      <form onSubmit={form.handleSubmit} className="auth-form">
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
        
        <div className="form-field-wrapper">
          <FormField
            icon={Mail}
            type="email"
            placeholder="Enter your email"
            error={form.errors.email}
            registration={form.register('email')}
          />
        </div>

        <FormField
          icon={Lock}
          type="password"
          placeholder="Enter your password"
          error={form.errors.password}
          registration={form.register('password')}
        />

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

        <LegalCheckbox 
          register={form.register} 
          error={form.errors.disclaimer}
          setValue={form.setValue}
        />

        {form.error && (
          <div className="auth-error">
            <p>{form.error}</p>
          </div>
        )}

        <button 
          type="submit" 
          className="submit-btn"
          disabled={form.isSubmitting}
        >
          {form.isSubmitting 
            ? 'Processing...' 
            : 'Sign Up'
          }
        </button>
      </form>
      <button 
        className="auth-toggle-btn"
        onClick={onSwitchToLogin}
      >
        Already have an account? Log in
      </button>
    </>
  );
}

export default SignupForm;