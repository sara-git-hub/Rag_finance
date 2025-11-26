import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Process from './pages/Process';
import IndexPage from './pages/IndexPage';
import Users from './pages/Users';
import Search from './pages/Search';
import QA from './pages/QA';
import AdminProjects from './pages/admin/AdminProjects';
import AdminAssets from './pages/admin/AdminAssets';
import AdminChunks from './pages/admin/AdminChunks';
import AdminConversations from './pages/admin/AdminConversations';
import AdminMessages from './pages/admin/AdminMessages';
import AdminVectors from './pages/admin/AdminVectors';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Routes publiques */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Routes protégées */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Pages admin */}
          <Route
            path="/upload"
            element={
              <ProtectedRoute requireAdmin>
                <Upload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/process"
            element={
              <ProtectedRoute requireAdmin>
                <Process />
              </ProtectedRoute>
            }
          />
          <Route
            path="/index"
            element={
              <ProtectedRoute requireAdmin>
                <IndexPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute requireAdmin>
                <Users />
              </ProtectedRoute>
            }
          />

          {/* Pages user + admin */}
          <Route
            path="/search"
            element={
              <ProtectedRoute>
                <Search />
              </ProtectedRoute>
            }
          />
          <Route
            path="/qa"
            element={
              <ProtectedRoute>
                <QA />
              </ProtectedRoute>
            }
          />

          {/* Admin management routes */}
          <Route
            path="/admin/projects"
            element={
              <ProtectedRoute requireAdmin>
                <AdminProjects />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/assets"
            element={
              <ProtectedRoute requireAdmin>
                <AdminAssets />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/chunks"
            element={
              <ProtectedRoute requireAdmin>
                <AdminChunks />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/conversations"
            element={
              <ProtectedRoute requireAdmin>
                <AdminConversations />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/messages"
            element={
              <ProtectedRoute requireAdmin>
                <AdminMessages />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/vectors"
            element={
              <ProtectedRoute requireAdmin>
                <AdminVectors />
              </ProtectedRoute>
            }
          />

          {/* Redirection par défaut */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
