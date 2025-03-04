// hooks/useAuthForm.js
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { authSchema } from '../utils/schema';

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

  const onSubmit = async (data) => {
    setError(null);
    setIsSubmitting(true);
    
    try {
      if (isLogin) {
        // Login flow
        const { error: signInError } = await signIn({
          email: data.email,
          password: data.password
        });
        
        if (signInError) {
          throw signInError;
        }
        
        onSignInSuccess();
      } else {
        // Signup flow - directly attempt signup without checking email
        const { data: signUpData, error: signUpError } = await signUp({
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
        
        // Call the backend API to add user to the database
        try {
          const response = await fetch('http://127.0.0.1:5000/api/newUser', {
            method: 'POST',
            mode: 'cors',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              userID: signUpData.user.id,
              email: data.email,
              fullName: data.fullName,
              preferredName: data.preferredName || data.fullName
            })
          });
          console.log(response);
          console.log('User data successfully sent to backend');
        } catch (apiError) {
          console.error('Error sending user data to backend:', apiError);
          // We don't throw here to avoid blocking the signup process
          // The user is already created in Supabase auth
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
    error,
    reset,
    setValue,
    getValues
  };
};