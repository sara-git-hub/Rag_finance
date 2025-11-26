import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminChunks = () => {
  const [chunks, setChunks] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    project_id: '',
    asset_id: ''
  });

  const columns = [
    { key: 'chunk_id', label: 'ID' },
    { key: 'project_id', label: 'Projet ID' },
    { key: 'asset_id', label: 'Fichier ID' },
    {
      key: 'chunk_text',
      label: 'Texte',
      render: (value) => value ? value.substring(0, 50) + '...' : 'N/A'
    },
    { key: 'chunk_index', label: 'Index' },
    {
      key: 'created_at',
      label: 'Créé le',
      render: (value) => new Date(value).toLocaleDateString('fr-FR')
    }
  ];

  const filterConfig = [
    {
      name: 'project_id',
      label: 'Projet ID',
      type: 'text',
      placeholder: 'Filtrer par projet...',
      value: filters.project_id
    },
    {
      name: 'asset_id',
      label: 'Fichier ID',
      type: 'text',
      placeholder: 'Filtrer par fichier...',
      value: filters.asset_id
    }
  ];

  const fetchChunks = async () => {
    setLoading(true);
    try {
      const projectId = filters.project_id || undefined;
      const assetId = filters.asset_id || undefined;
      const response = await adminAPI.getChunks(currentPage, 20, projectId, assetId);
      setChunks(response.data.chunks || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching chunks:', error);
      alert('Erreur lors du chargement des chunks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChunks();
  }, [currentPage, filters]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const handleDelete = async (chunk) => {
    await adminAPI.deleteChunk(chunk.chunk_id);
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <AdminTable
        title="Gestion des Chunks"
        columns={columns}
        data={chunks}
        totalPages={totalPages}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onDelete={handleDelete}
        onRefresh={fetchChunks}
        loading={loading}
        filters={filterConfig}
        onFilterChange={handleFilterChange}
      />
      </div>
    </>
  );
};

export default AdminChunks;
