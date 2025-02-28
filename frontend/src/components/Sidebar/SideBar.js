// components/Layout/SideBar.js
import React from 'react';
import { User, MessageSquare, LogOut, Menu, ChevronLeft } from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../Authentication/AuthContext';
import './SideBar.css';

function SideBar({ collapsed, onToggle }) {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  
  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/auth');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Toggle button with updated icon based on state */}
      <button className="sidebar-toggle-button" onClick={onToggle} aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
        {collapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
      </button>
      
      {/* Navigation Menu */}
      <div className="sidebar-menu">
        <NavLink to="/chat" className={({ isActive }) => 
          `sidebar-menu-item ${isActive ? 'sidebar-menu-item-active' : ''}`
        }>
          <MessageSquare size={20} />
          <span>Chat</span>
        </NavLink>
        
        
      </div>
      
      {/* Footer with user info and logout */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-avatar">
            <User size={18} />
          </div>
          <div className="sidebar-user-info">
            <span className="sidebar-user-label">Signed in as</span>
            <p className="sidebar-user-name">{user?.email || 'User'}</p>
          </div>
        </div>
        
        <button 
          className="sidebar-logout-link"
          onClick={handleLogout}
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}

export default SideBar;