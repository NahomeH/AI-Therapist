// Custom hook for form state & submission logic

import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { authSchema } from '../utils/schema';
import { useState } from 'react';

const defaultValues = {
  fullName: '',
  preferredName: '',
  email: '',
  password: '',
  confirmPassword: '',
  dateOfBirth: ''
};

export const useAuthForm = (isLogin, { onSignInSuccess, onSignUpSuccess, signIn, signUp }) => {
  const [error, setError] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    defaultValues,
    resolver: yupResolver(authSchema),
    mode: 'onChange',
    context: { isSignup: !isLogin }
  });

  const onSubmit = async (data) => {
    setError(null);
    try {
      if (isLogin) {
        const { error: signInError } = await signIn({
          email: data.email,
          password: data.password
        });
        if (signInError) throw signInError;
        onSignInSuccess();
      } else {
        const { error: signUpError } = await signUp({
          email: data.email,
          password: data.password,
          options: {
            data: {
              full_name: data.fullName,
              preferred_name: data.preferredName,
              date_of_birth: data.dateOfBirth
            }
          }
        });
        if (signUpError) throw signUpError;
        onSignUpSuccess();
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return {
    register,
    handleSubmit: handleSubmit(onSubmit),
    errors,
    isSubmitting,
    error,
    reset
  };
};