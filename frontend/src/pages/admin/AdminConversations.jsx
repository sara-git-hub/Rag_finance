import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    project_id: ''
  });

  const columns = [
    { key: 'conversation_id', label: 'ID' },
    { key: 'project_id', label: 'Projet ID' },
    { key: 'user_id', label: 'Utilisateur ID' },
    {
      key: 'message_count',
      label: 'Messages',
      render: (value) => value || 0
    },
    {
      key: 'created_at',
      label: 'Créée le',
      render: (value) => new Date(value).toLocaleDateString('fr-FR')
    },
    {
      key: 'updated_at',
      label: 'Mise à jour',
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
    }
  ];

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const projectId = filters.project_id || undefined;
      const response = await adminAPI.getConversations(currentPage, 20, projectId);
      setConversations(response.data.conversations || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      alert('Erreur lors du chargement des conversations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [currentPage, filters]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const handleDelete = async (conversation) => {
    await adminAPI.deleteConversation(conversation.conversation_id);
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <AdminTable
        title="Gestion des Conversations"
        columns={columns}
        data={conversations}
        totalPages={totalPages}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onDelete={handleDelete}
        onRefresh={fetchConversations}
        loading={loading}
        filters={filterConfig}
        onFilterChange={handleFilterChange}
      />
      </div>
    </>
  );
};

export default AdminConversations;
