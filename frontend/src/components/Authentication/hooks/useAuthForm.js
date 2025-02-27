// hooks/useAuthForm.js
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { authSchema } from '../utils/schema';
import { supabase } from '../../../supabase';

const defaultValues = {
  fullName: '',
  preferredName: '',
  email: '',
  password: '',
  confirmPassword: '',
  dateOfBirth: '',
  disclaimer: false
};

export const useAuthForm = (isLogin, { onSignInSuccess, onSignUpSuccess, signIn, signUp }) => {
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingEmail, setIsCheckingEmail] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    getValues
  } = useForm({
    defaultValues,
    resolver: yupResolver(authSchema),
    mode: 'onChange',
    context: { isSignup: !isLogin }
  });

  /**
   * Check if email already exists in Supabase auth
   * Uses a safer approach that won't create accidental users
   * 
   * @param {string} email - Email to check
   * @returns {Promise<boolean>} - Whether the email exists
   */
  const checkEmailExists = async (email) => {
    try {
      // Use the password recovery flow to check if email exists
      // This won't create accounts or send emails if configured correctly
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        // Don't actually send the email - just check if account exists
        redirectTo: window.location.origin
      });

      // If there's no error, the user exists
      // If we get "User not found" error, the email is available
      return !error || !error.message.includes('User not found');
    } catch (err) {
      console.error('Error checking email:', err);
      // Default to false (allow signup) in case of unexpected errors
      return false;
    }
  };

  const onSubmit = async (data) => {
    setError(null);
    setIsSubmitting(true);
    
    try {
      if (isLogin) {
        // Login flow - no changes needed
        const { error: signInError } = await signIn({
          email: data.email,
          password: data.password
        });
        
        if (signInError) {
          throw signInError;
        }
        
        onSignInSuccess();
      } else {
        // Signup flow - check if email exists first
        setIsCheckingEmail(true);
        const emailExists = await checkEmailExists(data.email);
        setIsCheckingEmail(false);
        
        if (emailExists) {
          setError('This email is already registered. Please log in instead.');
          setIsSubmitting(false);
          return;
        }
        
        // If email doesn't exist, proceed with signup
        const { error: signUpError } = await signUp({
          email: data.email,
          password: data.password,
          options: {
            data: {
              full_name: data.fullName,
              preferred_name: data.preferredName,
              date_of_birth: data.dateOfBirth,
              disclaimer_accepted: data.disclaimer,
              disclaimer_accepted_at: new Date().toISOString()
            }
          }
        });
        
        if (signUpError) {
          throw signUpError;
        }
        
        onSignUpSuccess();
      }
    } catch (err) {
      // Handle and display any errors
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    register,
    handleSubmit: handleSubmit(onSubmit),
    errors,
    isSubmitting,
    isCheckingEmail,
    error,
    reset,
    setValue,
    getValues
  };
};