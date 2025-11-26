import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import ConfirmModal from '../../components/admin/ConfirmModal';
import Navbar from '../../components/Navbar';

const AdminVectors = () => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, collection: null });
  const [deleting, setDeleting] = useState(false);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.getVectorCollections();
      setCollections(response.data.collections || []);
    } catch (error) {
      console.error('Error fetching collections:', error);
      alert('Erreur lors du chargement des collections');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, []);

  const handleDelete = async () => {
    if (!deleteModal.collection) return;

    setDeleting(true);
    try {
      await adminAPI.deleteCollection(deleteModal.collection.name);
      setDeleteModal({ isOpen: false, collection: null });
      fetchCollections();
    } catch (error) {
      console.error('Error deleting collection:', error);
      alert('Erreur lors de la suppression de la collection');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-xl p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Gestion des Collections Vectorielles</h2>
          <button
            onClick={fetchCollections}
            disabled={loading}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
          >
            {loading ? 'Chargement...' : 'Actualiser'}
          </button>
        </div>

        {/* Collections Grid */}
        {loading ? (
          <div className="text-center py-8 text-gray-500">Chargement...</div>
        ) : collections.length === 0 ? (
          <div className="text-center py-8 text-gray-500">Aucune collection</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((collection) => (
              <div
                key={collection.name}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">{collection.name}</h3>
                  <button
                    onClick={() => setDeleteModal({ isOpen: true, collection })}
                    className="text-red-600 hover:text-red-900 text-sm"
                  >
                    Supprimer
                  </button>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span className="font-medium">Vecteurs:</span>
                    <span>{collection.vectors_count?.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Dimension:</span>
                    <span>{collection.config?.params?.vectors?.size || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Distance:</span>
                    <span>{collection.config?.params?.vectors?.distance || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Delete Confirmation Modal */}
        <ConfirmModal
          isOpen={deleteModal.isOpen}
          onClose={() => setDeleteModal({ isOpen: false, collection: null })}
          onConfirm={handleDelete}
          title="Confirmer la suppression"
          message={`Êtes-vous sûr de vouloir supprimer la collection "${deleteModal.collection?.name}" ? Cette action est irréversible et supprimera tous les vecteurs de cette collection.`}
          isLoading={deleting}
        />
        </div>
      </div>
    </>
  );
};

export default AdminVectors;
