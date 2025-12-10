import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

const Dashboard = () => {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />

      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Bienvenue, {user?.username}!
          </h1>
          <p className="text-gray-600">
            {isAdmin()
              ? 'Vous êtes connecté en tant qu\'administrateur. Vous avez accès à toutes les fonctionnalités.'
              : 'Vous êtes connecté en tant qu\'utilisateur. Vous pouvez effectuer des recherches et poser des questions.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card: Recherche */}
          <div
            onClick={() => navigate('/search')}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
          >
            <div className="text-blue-500 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Recherche</h3>
            <p className="text-gray-600">Recherchez dans les documents indexés</p>
          </div>

          {/* Card: Questions/Réponses */}
          <div
            onClick={() => navigate('/qa')}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
          >
            <div className="text-green-500 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Questions/Réponses</h3>
            <p className="text-gray-600">Posez des questions sur vos documents</p>
          </div>

          {/* Card: Taux de Change */}
          <div
            onClick={() => navigate('/exchange-rates')}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
          >
            <div className="text-yellow-500 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Taux de Change</h3>
            <p className="text-gray-600">Consultez les taux de change MAD/EUR</p>
          </div>

          {/* Card Admin: Upload (visible seulement pour admin) */}
          {isAdmin() && (
            <>
              <div
                onClick={() => navigate('/upload')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-purple-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Upload Fichiers</h3>
                <p className="text-gray-600">Téléversez de nouveaux documents</p>
              </div>

              <div
                onClick={() => navigate('/process')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-orange-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Traitement</h3>
                <p className="text-gray-600">Traitez et découpez les documents</p>
              </div>

              <div
                onClick={() => navigate('/index')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-red-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Indexation</h3>
                <p className="text-gray-600">Indexez les documents dans la base vectorielle</p>
              </div>

              <div
                onClick={() => navigate('/users')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-pink-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Utilisateurs</h3>
                <p className="text-gray-600">Gérez les utilisateurs de la plateforme</p>
              </div>

              {/* New Admin Cards */}
              <div
                onClick={() => navigate('/admin/projects')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-indigo-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Projets</h3>
                <p className="text-gray-600">Gérez les projets de la plateforme</p>
              </div>

              <div
                onClick={() => navigate('/admin/assets')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-teal-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Assets</h3>
                <p className="text-gray-600">Gérez les fichiers et ressources</p>
              </div>

              <div
                onClick={() => navigate('/admin/chunks')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-cyan-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Chunks</h3>
                <p className="text-gray-600">Gérez les chunks de texte</p>
              </div>

              <div
                onClick={() => navigate('/admin/conversations')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-lime-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Conversations</h3>
                <p className="text-gray-600">Gérez les conversations utilisateurs</p>
              </div>

              <div
                onClick={() => navigate('/admin/messages')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-amber-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Messages</h3>
                <p className="text-gray-600">Gérez les messages des conversations</p>
              </div>

              <div
                onClick={() => navigate('/admin/vectors')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-violet-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Gestion Vecteurs</h3>
                <p className="text-gray-600">Gérez les collections vectorielles</p>
              </div>

              <div
                onClick={() => navigate('/admin/exchange-rates')}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200 cursor-pointer"
              >
                <div className="text-emerald-500 mb-4">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Admin Taux de Change</h3>
                <p className="text-gray-600">Administration des taux de change</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
