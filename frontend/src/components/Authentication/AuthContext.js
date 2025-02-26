// Manages global auth state (user session, login/logout)

import { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../../supabase';

// Create context with default values
const AuthContext = createContext({});

export function AuthProvider({ children }) {
  // Track authenticated user and loading state
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session when component mounts
    const session = supabase.auth.getSession();
    setUser(session?.user ?? null);
    setLoading(false);

    // Subscribe to auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      // Update user state when auth state changes
      setUser(session?.user ?? null);
    });

    // Cleanup subscription on unmount
    return () => subscription.unsubscribe();
  }, []);

  // Values provided to consuming components
  const value = {
    user,      // Current authenticated user
    loading,   // Loading state for initial auth check
    signUp: (data) => supabase.auth.signUp(data),
    signIn: (data) => supabase.auth.signInWithPassword(data),
    signOut: () => supabase.auth.signOut()
  };

  return (
    <AuthContext.Provider value={value}>
      {/* Only render children once initial auth check is complete */}
      {!loading && children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to use authentication context
 * 
 * @throws {Error} If used outside of AuthProvider
 * @returns {Object} Auth context value
 * 
 * Usage:
 * const { user, signIn, signUp, signOut } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}