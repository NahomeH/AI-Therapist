// Form validation rules using Yup
import * as yup from 'yup';

export const authSchema = yup.object().shape({
  email: yup.string()
    .when('$isSignup', {
      is: true,
      then: (schema) => schema
        .required('Email is required')
        .email('Must be a valid email')
    }),
  password: yup.string()
    .when('$isSignup', {
      is: true,
      then: (schema) => schema
        .required('Password is required')
        .min(8, 'Must be at least 8 characters')
        .matches(/[A-Z]/, 'Must contain an uppercase letter')
        .matches(/[a-z]/, 'Must contain a lowercase letter')
        .matches(/[0-9]/, 'Must contain a number')
        .matches(/[!@#$%^&*(),.?":{}|<>]/, 'Must contain a special character')
    }),
  // Other signup fields remain the same
  fullName: yup.string()
    .when('$isSignup', {
      is: true,
      then: schema => schema.required('Full name is required')
    }),
  preferredName: yup.string(),
  confirmPassword: yup.string()
    .when('$isSignup', {
      is: true,
      then: schema => schema.required('Please confirm your password')
        .oneOf([yup.ref('password')], 'Passwords must match')
    }),
  dateOfBirth: yup.string()
    .when('$isSignup', {
      is: true,
      then: schema => schema.required('Date of birth is required')
    })
});