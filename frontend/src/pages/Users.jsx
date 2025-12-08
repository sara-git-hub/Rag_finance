import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import Navbar from '../components/Navbar';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showAddForm, setShowAddForm] = useState(false);
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'user' });
  const [passwordModal, setPasswordModal] = useState({ show: false, username: '', newPassword: '' });
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    fetchUsers();
    // Get current logged-in user
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await authAPI.getAllUsers();
      setUsers(response.data);
      setMessage({ type: 'success', text: `${response.data.length} utilisateur(s) chargé(s)` });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Erreur lors du chargement des utilisateurs'
      });
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'user':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusBadgeColor = (isActive) => {
    return isActive
      ? 'bg-green-100 text-green-800 border-green-200'
      : 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authAPI.createUser(newUser);
      setMessage({ type: 'success', text: `Utilisateur ${newUser.username} créé avec succès` });
      setNewUser({ username: '', email: '', password: '', role: 'user' });
      setShowAddForm(false);
      await fetchUsers();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Erreur lors de la création de l\'utilisateur'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (username) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${username} ?`)) {
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authAPI.deleteUser(username);
      setMessage({ type: 'success', text: `Utilisateur ${username} supprimé avec succès` });
      await fetchUsers();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Erreur lors de la suppression de l\'utilisateur'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePassword = async () => {
    if (!passwordModal.newPassword) {
      setMessage({ type: 'error', text: 'Veuillez entrer un nouveau mot de passe' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authAPI.updateUserPassword(passwordModal.username, passwordModal.newPassword);
      setMessage({ type: 'success', text: `Mot de passe de ${passwordModal.username} modifié avec succès` });
      setPasswordModal({ show: false, username: '', newPassword: '' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Erreur lors de la modification du mot de passe'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-gray-800">Gestion des Utilisateurs</h1>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowAddForm(!showAddForm)}
                  className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition duration-200 font-semibold"
                >
                  {showAddForm ? 'Annuler' : '+ Ajouter un utilisateur'}
                </button>
                <button
                  onClick={fetchUsers}
                  disabled={loading}
                  className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition duration-200 font-semibold disabled:opacity-50"
                >
                  {loading ? 'Chargement...' : 'Actualiser'}
                </button>
              </div>
            </div>

            {/* Add User Form */}
            {showAddForm && (
              <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Créer un nouvel utilisateur</h2>
                <form onSubmit={handleAddUser} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom d'utilisateur *
                      </label>
                      <input
                        type="text"
                        required
                        value={newUser.username}
                        onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="username"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email *
                      </label>
                      <input
                        type="email"
                        required
                        value={newUser.email}
                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="email@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Mot de passe *
                      </label>
                      <input
                        type="password"
                        required
                        value={newUser.password}
                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="••••••••"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Rôle *
                      </label>
                      <select
                        value={newUser.role}
                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="user">user</option>
                        <option value="admin">admin</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddForm(false);
                        setNewUser({ username: '', email: '', password: '', role: 'user' });
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition duration-200"
                    >
                      Annuler
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition duration-200 font-semibold disabled:opacity-50"
                    >
                      Créer l'utilisateur
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Message Display */}
            {message.text && (
              <div className={`mb-6 p-4 rounded-lg ${
                message.type === 'success'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : 'bg-red-100 text-red-800 border border-red-200'
              }`}>
                <p className="font-medium">{message.text}</p>
              </div>
            )}

            {/* Loading State */}
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              </div>
            ) : (
              <>
                {/* Users Table */}
                {users.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b-2 border-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Nom d'utilisateur
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Email
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rôle
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Statut
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {users.map((user, index) => (
                          <tr key={index} className="hover:bg-gray-50 transition">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">{user.username}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-700">{user.email}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getRoleBadgeColor(user.role)}`}>
                                {user.role.toUpperCase()}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusBadgeColor(user.is_active)}`}>
                                {user.is_active ? 'Actif' : 'Inactif'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => setPasswordModal({ show: true, username: user.username, newPassword: '' })}
                                  className="px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600 transition"
                                  title="Modifier le mot de passe"
                                >
                                  🔑 Mot de passe
                                </button>
                                <button
                                  onClick={() => handleDeleteUser(user.username)}
                                  disabled={currentUser?.username === user.username}
                                  className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                  title={currentUser?.username === user.username ? "Vous ne pouvez pas vous supprimer vous-même" : "Supprimer l'utilisateur"}
                                >
                                  🗑️ Supprimer
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">Aucun utilisateur trouvé</p>
                  </div>
                )}

                {/* Statistics */}
                {users.length > 0 && (
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <h3 className="text-sm font-medium text-gray-600 mb-1">Total Utilisateurs</h3>
                      <p className="text-2xl font-bold text-gray-800">{users.length}</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                      <h3 className="text-sm font-medium text-gray-600 mb-1">Administrateurs</h3>
                      <p className="text-2xl font-bold text-gray-800">
                        {users.filter(u => u.role === 'admin').length}
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h3 className="text-sm font-medium text-gray-600 mb-1">Utilisateurs Actifs</h3>
                      <p className="text-2xl font-bold text-gray-800">
                        {users.filter(u => u.is_active).length}
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Password Update Modal */}
      {passwordModal.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Modifier le mot de passe
            </h2>
            <p className="text-gray-600 mb-4">
              Utilisateur : <span className="font-semibold">{passwordModal.username}</span>
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nouveau mot de passe
              </label>
              <input
                type="password"
                value={passwordModal.newPassword}
                onChange={(e) => setPasswordModal({ ...passwordModal, newPassword: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Entrez le nouveau mot de passe"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setPasswordModal({ show: false, username: '', newPassword: '' })}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Annuler
              </button>
              <button
                onClick={handleUpdatePassword}
                disabled={loading || !passwordModal.newPassword}
                className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition disabled:opacity-50"
              >
                Mettre à jour
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
