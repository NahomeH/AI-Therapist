/**
 * @fileoverview Agent Preferences component for the Talk2Me therapy chatbot application.
 * This component allows users to set their therapy preferences including
 * information they want the therapist to know, therapy style preferences,
 * and therapist gender preference.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../Authentication/AuthContext';
import './AgentPreferences.css';

function AgentPreferences() {
  const { user } = useAuth();
  const [therapistInfo, setTherapistInfo] = useState('');
  const [therapyPreferences, setTherapyPreferences] = useState('');
  const [therapistGender, setTherapistGender] = useState('female');
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');

  // Load saved preferences when component mounts
  useEffect(() => {
    const loadPreferences = async () => {
      if (!user) return;
      
      try {
        // Here we fetch the user's preferences from the backend
        // For now, we'll use localStorage as a placeholder
        const savedInfo = localStorage.getItem('therapistInfo');
        const savedPreferences = localStorage.getItem('therapyPreferences');
        const savedGender = localStorage.getItem('therapistGender');
        
        if (savedInfo) setTherapistInfo(savedInfo);
        if (savedPreferences) setTherapyPreferences(savedPreferences);
        if (savedGender) setTherapistGender(savedGender);
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    };
    
    loadPreferences();
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveStatus('');
    
    try {
      // Here we save the preferences to the backend
      // For now, we'll use localStorage as a placeholder
      localStorage.setItem('therapistInfo', therapistInfo);
      localStorage.setItem('therapyPreferences', therapyPreferences);
      localStorage.setItem('therapistGender', therapistGender);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveStatus('Preferences saved successfully!');
    } catch (error) {
      console.error('Error saving preferences:', error);
      setSaveStatus('Error saving preferences. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="agent-preferences-container">
      <div className="agent-preferences-header">
        <h1>Agent Preferences</h1>
        <p>Customize your therapy experience by setting your preferences below.</p>
      </div>
      
      <form className="agent-preferences-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="therapistInfo">
            Is there any information you would like our therapist to know?
          </label>
          <textarea
            id="therapistInfo"
            value={therapistInfo}
            onChange={(e) => setTherapistInfo(e.target.value)}
            placeholder="I think I might have ADHD, but I'm not diagnosed."
            rows={4}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="therapyPreferences">
            What are your therapy preferences?
          </label>
          <textarea
            id="therapyPreferences"
            value={therapyPreferences}
            onChange={(e) => setTherapyPreferences(e.target.value)}
            placeholder="I prefer a therapist who is very empathetic and patient with me."
            rows={4}
          />
        </div>
        
        <div className="form-group">
          <label>Do you prefer a male or female therapist?</label>
          <div className="radio-group">
            <div className="radio-option">
              <input
                type="radio"
                id="male"
                name="therapistGender"
                value="male"
                checked={therapistGender === 'male'}
                onChange={() => setTherapistGender('male')}
              />
              <label htmlFor="male">Male</label>
            </div>
            
            <div className="radio-option">
              <input
                type="radio"
                id="female"
                name="therapistGender"
                value="female"
                checked={therapistGender === 'female'}
                onChange={() => setTherapistGender('female')}
              />
              <label htmlFor="female">Female</label>
            </div>
            
          </div>
        </div>
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="save-button"
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Preferences'}
          </button>
          
          {saveStatus && (
            <div className={`save-status ${saveStatus.includes('Error') ? 'error' : 'success'}`}>
              {saveStatus}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default AgentPreferences;
