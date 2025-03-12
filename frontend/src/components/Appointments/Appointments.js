import React, { useState, useEffect } from 'react';
import { useAuth } from '../Authentication/AuthContext';
import { formatInTimeZone } from 'date-fns-tz';
import { Calendar, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Appointments.css';

function Appointments() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/appointments`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId: user?.id
          })
        });
        
        const data = await response.json();
        if (data.success) {
          setAppointments(data.appointments || []);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError('Failed to fetch appointments');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) {
      fetchAppointments();
    }
  }, [user]);

  const handleScheduleChat = () => {
    // Navigate to chat interface
    // window.location.href = '/chat';
    navigate('/chat');
  };

  if (loading) {
    return (
      <div className="appointments-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="appointments-container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="appointments-container">
      <h1>Your Appointments</h1>
      
      {appointments.length === 0 ? (
        <div className="no-appointments">
          <div className="no-appointments-content">
            <Calendar size={48} />
            <h2>No Upcoming Appointments</h2>
            <p>Start a chat session with Jennifer to schedule your next appointment.</p>
            <button onClick={handleScheduleChat} className="schedule-button">
              Start Chat Session
            </button>
          </div>
        </div>
      ) : (
        <div className="appointments-list">
          {appointments.map((appointment, index) => (
            <div key={index} className="appointment-card">
              <div className="appointment-header">
                <Calendar size={24} />
                <h3>Therapy Session with Jennifer</h3>
              </div>
              <div className="appointment-details">
                <div className="appointment-date">
                  {formatInTimeZone(
                    new Date(appointment.appointment_time),
                    'America/Los_Angeles',
                    'EEEE, MMMM d, yyyy'
                  )}
                </div>
                <div className="appointment-time">
                  <Clock size={16} />
                  {formatInTimeZone(
                    new Date(appointment.appointment_time),
                    'America/Los_Angeles',
                    'h:mm a'
                  )} PT
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Appointments;