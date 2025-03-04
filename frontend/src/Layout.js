// components/Layout/Layout.js
import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import SideBar from './components/Sidebar/SideBar';
import Header from './components/Header/Header';
import './Layout.css';

function Layout() {
  // State to track sidebar visibility
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Function to toggle sidebar visibility
  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
    // Optionally store preference in localStorage
    localStorage.setItem('sidebarCollapsed', (!sidebarCollapsed).toString());
  };
  
  // Load user preference on initial render
  useEffect(() => {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState !== null) {
      setSidebarCollapsed(savedState === 'true');
    }
  }, []);

  return (
    <>
      <SideBar 
        collapsed={sidebarCollapsed} 
        onToggle={toggleSidebar} 
      />
      <div className={`layout-main ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Header />
        <main className="layout-content">
          <Outlet />
        </main>
      </div>
    </>
  );
}

export default Layout;