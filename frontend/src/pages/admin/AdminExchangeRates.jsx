import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import Navbar from '../../components/Navbar';

const AdminExchangeRates = () => {
  const [loading, setLoading] = useState(false);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [trainResult, setTrainResult] = useState(null);
  const [selectedPair, setSelectedPair] = useState('MAD/EUR');

  const currencyPairs = ['MAD/EUR', 'MAD/USD'];

  useEffect(() => {
    fetchSchedulerStatus();
  }, []);

  const fetchSchedulerStatus = async () => {
    try {
      const response = await adminAPI.getSchedulerStatus();
      setSchedulerStatus(response.data);
    } catch (error) {
      console.error('Error fetching scheduler status:', error);
    }
  };

  const handleFetchRatesNow = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.fetchRatesNow();
      alert(`Taux récupérés avec succès!\nMAD/EUR: ${response.data.results['MAD/EUR'] ? 'OK' : 'Échec'}\nMAD/USD: ${response.data.results['MAD/USD'] ? 'OK' : 'Échec'}`);
    } catch (error) {
      console.error('Error fetching rates:', error);
      alert('Erreur lors de la récupération des taux');
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    setLoading(true);
    setTrainResult(null);
    try {
      const response = await adminAPI.trainExchangeModel(selectedPair, 175);
      setTrainResult(response.data.data);
      alert(`Modèle ${selectedPair} entraîné avec succès!\nMAE: ${response.data.data.metrics.mae.toFixed(4)}\nRMSE: ${response.data.data.metrics.rmse.toFixed(4)}\nR²: ${response.data.data.metrics.r2.toFixed(4)}`);
    } catch (error) {
      console.error('Error training model:', error);
      alert('Erreur lors de l\'entraînement du modèle');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePredictions = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.generatePredictions(selectedPair, 7);
      alert(`${response.data.predictions_saved} prédictions générées pour ${selectedPair}`);
    } catch (error) {
      console.error('Error generating predictions:', error);
      if (error.response?.status === 404) {
        alert('Modèle non trouvé. Veuillez d\'abord entraîner le modèle.');
      } else {
        alert('Erreur lors de la génération des prédictions');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            Gestion des Taux de Change
          </h1>

          {/* Scheduler Status */}
          <div className="mb-8 p-4 bg-blue-50 rounded-lg">
            <h2 className="text-xl font-semibold text-gray-700 mb-3">
              Statut du Scheduler
            </h2>
            {schedulerStatus ? (
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium">État:</span>{' '}
                  <span className={`px-2 py-1 rounded ${schedulerStatus.status === 'running' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                    {schedulerStatus.status === 'running' ? 'En cours' : 'Arrêté'}
                  </span>
                </p>
                {schedulerStatus.jobs && schedulerStatus.jobs.length > 0 && (
                  <div>
                    <p className="font-medium text-gray-700 mt-3">Jobs planifiés:</p>
                    {schedulerStatus.jobs.map((job, idx) => (
                      <div key={idx} className="ml-4 mt-2 text-sm text-gray-600">
                        <p><strong>{job.name}</strong></p>
                        <p>Prochaine exécution: {job.next_run ? new Date(job.next_run).toLocaleString('fr-FR') : 'N/A'}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">Chargement...</p>
            )}
          </div>

          {/* Manual Actions */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Actions Manuelles
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <button
                onClick={handleFetchRatesNow}
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Récupération...' : 'Récupérer les taux maintenant'}
              </button>
            </div>
          </div>

          {/* Model Training */}
          <div className="mb-8 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Entraînement du Modèle ML
            </h2>

            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">
                Paire de devises
              </label>
              <select
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {currencyPairs.map(pair => (
                  <option key={pair} value={pair}>{pair}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={handleTrainModel}
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
              >
                {loading ? 'Entraînement...' : `Entraîner le modèle ${selectedPair}`}
              </button>

              <button
                onClick={handleGeneratePredictions}
                disabled={loading}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
              >
                {loading ? 'Génération...' : 'Générer les prédictions (7 jours)'}
              </button>
            </div>

            {/* Training Results */}
            {trainResult && (
              <div className="mt-6 p-4 bg-white border border-green-300 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  Résultats de l'entraînement
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">MAE</p>
                    <p className="text-lg font-bold text-gray-800">{trainResult.metrics.mae.toFixed(4)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">RMSE</p>
                    <p className="text-lg font-bold text-gray-800">{trainResult.metrics.rmse.toFixed(4)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">MAPE (%)</p>
                    <p className="text-lg font-bold text-gray-800">{(trainResult.metrics.mape * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Échantillons</p>
                    <p className="text-lg font-bold text-gray-800">{trainResult.training_samples}</p>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-600">
                  <p>Période: {trainResult.date_range.start} → {trainResult.date_range.end}</p>
                  <p>Époques: {trainResult.metrics.epochs_trained}</p>
                </div>
              </div>
            )}
          </div>

          {/* Info Box */}
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">ℹ️ Informations</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Le scheduler récupère automatiquement les taux tous les jours à 9h (heure de Casablanca)</li>
              <li>• Le modèle LSTM utilise 30 jours d'historique pour prédire les 7 prochains jours</li>
              <li>• Les prédictions sont sauvegardées en base de données pour consultation par les utilisateurs</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminExchangeRates;
