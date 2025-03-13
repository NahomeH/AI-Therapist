/**
 * @fileoverview Dashboard component for the Talk2Me therapy chatbot application.
 * This component serves as the main landing page after authentication,
 * providing quick access to all main features of the application.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../Authentication/AuthContext';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, CalendarPlus, Settings } from 'lucide-react';
import './Dashboard.css';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [greeting, setGreeting] = useState('');
  const userName = user?.user_metadata?.preferred_name || 'there';

  // Set greeting based on time of day
  useEffect(() => {
    const currentHour = new Date().getHours();
    
    if (currentHour >= 5 && currentHour < 12) {
      setGreeting('Good morning');
    } else if (currentHour >= 12 && currentHour < 18) {
      setGreeting('Good afternoon');
    } else {
      setGreeting('Good evening');
    }
  }, []);

  // Navigation handlers
  const navigateToChat = () => navigate('/chat');
  const navigateToAppointments = () => navigate('/appointments');
  const navigateToPreferences = () => navigate('/preferences');

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>{greeting}, {userName}!</h1>
        <p>Welcome to Talk2Me, your personal therapy assistant.</p>
      </div>

      <div className="dashboard-widgets">
        <div className="dashboard-widget" onClick={navigateToChat}>
          <div className="widget-icon chat-icon">
            <MessageSquare size={32} />
          </div>
          <div className="widget-content">
            <h2>Start a Therapy Session</h2>
            <p>Begin a conversation with your AI therapist to discuss your thoughts and feelings.</p>
          </div>
        </div>

        <div className="dashboard-widget" onClick={navigateToAppointments}>
          <div className="widget-icon appointments-icon">
            <CalendarPlus size={32} />
          </div>
          <div className="widget-content">
            <h2>Manage Appointments</h2>
            <p>View and manage your scheduled therapy sessions.</p>
          </div>
        </div>

        <div className="dashboard-widget" onClick={navigateToPreferences}>
          <div className="widget-icon preferences-icon">
            <Settings size={32} />
          </div>
          <div className="widget-content">
            <h2>Agent Preferences</h2>
            <p>Customize your therapy experience by setting your preferences.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
