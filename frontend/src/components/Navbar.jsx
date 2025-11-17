import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Menu pour les utilisateurs normaux
  const userMenuItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/search', label: 'Recherche' },
    { path: '/qa', label: 'Questions/Réponses' },
  ];

  // Menu pour les administrateurs (toutes les fonctionnalités)
  const adminMenuItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/upload', label: 'Upload Fichiers' },
    { path: '/process', label: 'Traitement' },
    { path: '/index', label: 'Indexation' },
    { path: '/search', label: 'Recherche' },
    { path: '/qa', label: 'Questions/Réponses' },
    { path: '/users', label: 'Gestion Utilisateurs' },
  ];

  const menuItems = isAdmin() ? adminMenuItems : userMenuItems;

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="text-2xl font-bold">
              RAG Finance
            </Link>
          </div>

          {/* Menu Items */}
          <div className="hidden md:flex space-x-1">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="px-4 py-2 rounded-md hover:bg-white hover:bg-opacity-20 transition duration-200"
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
                <span className="text-sm font-semibold">{user?.username}</span>
              </div>
              <span className={`text-xs px-2 py-1 rounded ${
                isAdmin() ? 'bg-yellow-500' : 'bg-green-500'
              }`}>
                {isAdmin() ? 'Admin' : 'User'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-md transition duration-200"
            >
              Déconnexion
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <div className="md:hidden pb-4">
          <div className="flex flex-col space-y-2">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="px-4 py-2 rounded-md hover:bg-white hover:bg-opacity-20 transition duration-200"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
