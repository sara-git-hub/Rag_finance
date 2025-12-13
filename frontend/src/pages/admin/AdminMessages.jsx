import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminTable from '../../components/admin/AdminTable';
import Navbar from '../../components/Navbar';

const AdminMessages = () => {
  const [messages, setMessages] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    conversation_id: ''
  });

  const columns = [
    { key: 'message_id', label: 'ID' },
    { key: 'conversation_id', label: 'Conversation ID' },
    {
      key: 'role',
      label: 'Rôle',
      render: (value) => {
        const badges = {
          user: 'bg-blue-100 text-blue-800',
          assistant: 'bg-green-100 text-green-800',
          system: 'bg-gray-100 text-gray-800'
        };
        return (
          <span className={`px-2 py-1 rounded-full text-xs ${badges[value] || 'bg-gray-100'}`}>
            {value}
          </span>
        );
      }
    },
    {
      key: 'content',
      label: 'Contenu',
      render: (value) => value ? value.substring(0, 50) + '...' : 'N/A'
    },
    {
      key: 'created_at',
      label: 'Créé le',
      render: (value) => new Date(value).toLocaleDateString('fr-FR')
    }
  ];

  const filterConfig = [
    {
      name: 'conversation_id',
      label: 'Conversation ID',
      type: 'text',
      placeholder: 'Filtrer par conversation...',
      value: filters.conversation_id
    }
  ];

  const fetchMessages = async () => {
    setLoading(true);
    try {
      const conversationId = filters.conversation_id || undefined;
      const response = await adminAPI.getMessages(currentPage, 20, conversationId);
      setMessages(response.data.messages || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching messages:', error);
      alert('Erreur lors du chargement des messages');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [currentPage, filters]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const handleDelete = async (message) => {
    await adminAPI.deleteMessage(message.message_id);
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <AdminTable
        title="Gestion des Messages"
        columns={columns}
        data={messages}
        totalPages={totalPages}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onDelete={handleDelete}
        onRefresh={fetchMessages}
        loading={loading}
        filters={filterConfig}
        onFilterChange={handleFilterChange}
      />
      </div>
    </>
  );
};

export default AdminMessages;
