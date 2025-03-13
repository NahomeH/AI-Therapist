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
  const [therapistGender, setTherapistGender] = useState('FEMALE');
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');

  // Load saved preferences when component mounts
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/get-prefs', {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId: user?.id || 'anonymous'
          })
        });
        const data = await response.json();
        console.log('Get preferences data:', data);
        setTherapistInfo(data?.backgroundInfo || '');
        setTherapyPreferences(data?.agentPreferences || '');
        setTherapistGender(data.gender);
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
      const response = await fetch('http://127.0.0.1:5000/api/set-prefs', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user?.id || 'anonymous',
          backgroundInfo: therapistInfo,
          agentPreferences: therapyPreferences,
          gender: therapistGender
        })
      });
      const data = await response.json();
      console.log('Set preferences response:', data);
      // Add a 1-second delay for realism
      setTimeout(() => {
        setSaveStatus('Preferences saved successfully!');
        setIsSaving(false); // Move this inside the setTimeout callback
      }, 1000);
    } catch (error) {
      console.error('Error saving preferences:', error);
      setSaveStatus('Failed to save preferences. Please try again.');
      setIsSaving(false); // Keep this here for the error case
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
                value="MALE"
                checked={therapistGender === 'MALE'}
                onChange={() => setTherapistGender('MALE')}
              />
              <label htmlFor="male">Male</label>
            </div>
            
            <div className="radio-option">
              <input
                type="radio"
                id="female"
                name="therapistGender"
                value="FEMALE"
                checked={therapistGender === 'FEMALE'}
                onChange={() => setTherapistGender('FEMALE')}
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
