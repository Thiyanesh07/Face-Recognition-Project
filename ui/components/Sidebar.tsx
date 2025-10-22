import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// FIX: Removed unused 'path' prop. The component only needs to render its children.
const NavIcon = ({ children }: { children: React.ReactNode }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    {children}
  </svg>
);

const Sidebar: React.FC = () => {
  const { logout } = useAuth();
  const location = useLocation();
  
  const navItems = [
    { path: '/dashboard', name: 'Dashboard', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /> },
    { path: '/attendance', name: 'Attendance Log', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /> },
    { path: '/students', name: 'Manage Students', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21a6 6 0 00-9-5.197m0 0A5.975 5.975 0 0112 13a5.975 5.975 0 013 1.803" /> },
    { path: '/cameras', name: 'Manage Cameras', icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /> },
  ];

  const getNavLinkClass = (path: string) => {
    return location.pathname === path
      ? 'bg-primary text-white'
      : 'text-sidebar-text hover:bg-sidebar-hover hover:text-white';
  };

  return (
    <div className="flex flex-col w-64 bg-sidebar text-white">
      <div className="flex items-center justify-center h-20 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">Attendance</h1>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-2">
        {navItems.map(item => (
          <NavLink
            key={item.name}
            to={item.path}
            className={`flex items-center px-4 py-2 rounded-lg transition-colors duration-200 ${getNavLinkClass(item.path)}`}
          >
            {/* FIX: Removed unused 'path' prop from the component call to match the updated definition. */}
            <NavIcon>{item.icon}</NavIcon>
            <span className="ml-3">{item.name}</span>
          </NavLink>
        ))}
      </nav>
      <div className="px-2 py-4">
        <button
          onClick={logout}
          className="w-full flex items-center px-4 py-2 text-sidebar-text rounded-lg hover:bg-red-500 hover:text-white transition-colors duration-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span className="ml-3">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
