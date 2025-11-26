import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminProjects = () => {
  const [projects, setProjects] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const columns = [
    { key: 'project_id', label: 'ID' },
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
        onRefresh={fetchProjects}
        loading={loading}
      />
      </div>
    </>
  );
};

export default AdminProjects;
