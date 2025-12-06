import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminProjects = () => {
  const [projects, setProjects] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [editModal, setEditModal] = useState({ isOpen: false, project: null });
  const [editName, setEditName] = useState('');
  const [saving, setSaving] = useState(false);

  const columns = [
    { key: 'project_id', label: 'ID' },
    {
      key: 'project_name',
      label: 'Nom',
      render: (value) => value || '(Sans nom)'
    },
    { key: 'project_language', label: 'Langue' },
    {
      key: 'file_count',
      label: 'Fichiers',
      render: (value) => value || 0
    },
    {
      key: 'created_at',
      label: 'Créé le',
      render: (value) => new Date(value).toLocaleDateString('fr-FR')
    }
  ];

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.getProjects(currentPage, 20);
      setProjects(response.data.projects || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching projects:', error);
      alert('Erreur lors du chargement des projets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [currentPage]);

  const handleDelete = async (project) => {
    await adminAPI.deleteProject(project.project_id);
  };

  const handleEdit = (project) => {
    setEditModal({ isOpen: true, project });
    setEditName(project.project_name || '');
  };

  const handleSaveName = async () => {
    if (!editModal.project) return;

    setSaving(true);
    try {
      await adminAPI.updateProjectName(editModal.project.project_id, editName);
      setEditModal({ isOpen: false, project: null });
      fetchProjects();
    } catch (error) {
      console.error('Error updating project name:', error);
      alert('Erreur lors de la mise à jour du nom');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <AdminTable
        title="Gestion des Projets"
        columns={columns}
        data={projects}
        totalPages={totalPages}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onDelete={handleDelete}
        onEdit={handleEdit}
        onRefresh={fetchProjects}
        loading={loading}
      />

      {/* Edit Name Modal */}
      {editModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">Modifier le nom du projet</h3>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Nom du projet"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setEditModal({ isOpen: false, project: null })}
                disabled={saving}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                onClick={handleSaveName}
                disabled={saving}
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
};

export default AdminProjects;
