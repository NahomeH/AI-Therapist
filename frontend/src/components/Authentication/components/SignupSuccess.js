// Success message component after signup

import React from 'react';
import { CheckCircle2 } from 'lucide-react';

const SignupSuccess = ({ onLoginClick }) => (
  <div className="app-container">
    <div className="auth-window">
      <h2 className="auth-title">Welcome to Talk2Me</h2>
      <div className="auth-form-container">
        <div className="auth-success-content">
          <div className="success-icon">
            <CheckCircle2 size={48} className="text-green-500" />
          </div>
          <h3 className="text-xl font-semibold mb-4 text-center">
            Successfully signed up!
          </h3>
          <p className="text-center mb-2">
            Please check your email to verify your account.
          </p>
          <p className="text-center mb-6">
            Once verified, you can log in.
          </p>
          <button 
            className="submit-btn w-full"
            onClick={onLoginClick}
          >
            Go to Login
          </button>
        </div>
      </div>
    </div>
  </div>
);

export default SignupSuccess;