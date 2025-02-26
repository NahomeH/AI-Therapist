// Reusable input component with icon & error handling

import React from 'react';

const FormField = ({
  icon: Icon,
  error,
  type = "text",
  placeholder,
  registration,
  className = "",
  ...props
}) => (
  <div className={`form-group ${error ? 'has-error' : ''}`}>
    <div className="input-with-icon">
      <Icon size={20} className="input-icon" />
      <input
        type={type}
        placeholder={placeholder}
        className={`form-input ${error ? 'error' : ''} ${className}`}
        {...registration}
        {...props}
      />
    </div>
    {error && (
      <span className="error-message">
        {error.message}
      </span>
    )}
  </div>
);

export default FormField;