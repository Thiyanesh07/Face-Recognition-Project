
import React from 'react';
import { useLocation } from 'react-router-dom';

const Header: React.FC = () => {
    const location = useLocation();
    
    const getTitle = () => {
        switch (location.pathname) {
            case '/dashboard':
                return 'Dashboard';
            case '/attendance':
                return 'Attendance Log';
            case '/students':
                return 'Manage Students';
            case '/cameras':
                return 'Manage Cameras';
            default:
                return 'Attendance System';
        }
    };

    return (
        <header className="bg-white shadow-md p-4">
            <h1 className="text-2xl font-semibold text-gray-800">{getTitle()}</h1>
        </header>
    );
};

export default Header;
