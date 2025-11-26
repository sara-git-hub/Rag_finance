import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminAssets = () => {
  const [assets, setAssets] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    project_id: '',
    asset_type: ''
  });

  const columns = [
    { key: 'asset_id', label: 'ID' },
    { key: 'project_id', label: 'Projet ID' },
    { key: 'asset_name', label: 'Nom' },
    { key: 'asset_type', label: 'Type' },
    {
      key: 'asset_size',
      label: 'Taille',
      render: (value) => value ? `${(value / 1024 / 1024).toFixed(2)} MB` : 'N/A'
    },
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
      name: 'asset_type',
      label: 'Type',
      type: 'select',
      value: filters.asset_type,
      options: [
        { value: 'pdf', label: 'PDF' },
        { value: 'docx', label: 'DOCX' },
        { value: 'txt', label: 'TXT' }
      ]
    }
  ];

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const projectId = filters.project_id || undefined;
      const assetType = filters.asset_type || undefined;
      const response = await adminAPI.getAssets(currentPage, 20, projectId, assetType);
      setAssets(response.data.assets || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching assets:', error);
      alert('Erreur lors du chargement des fichiers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, [currentPage, filters]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const handleDelete = async (asset) => {
    await adminAPI.deleteAsset(asset.asset_id);
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <AdminTable
        title="Gestion des Fichiers"
        columns={columns}
        data={assets}
        totalPages={totalPages}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onDelete={handleDelete}
        onRefresh={fetchAssets}
        loading={loading}
        filters={filterConfig}
        onFilterChange={handleFilterChange}
      />
      </div>
    </>
  );
};

export default AdminAssets;
