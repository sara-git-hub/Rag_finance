import React, { useState, useEffect } from 'react';
import { publicAPI } from '../services/api';
import Navbar from '../components/Navbar';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const ExchangeRates = () => {
  const [loading, setLoading] = useState(false);
  const [latestRates, setLatestRates] = useState(null);
  const [selectedPair, setSelectedPair] = useState('MAD/EUR');
  const [chartData, setChartData] = useState([]);
  const [daysHistory, setDaysHistory] = useState(30);
  const [error, setError] = useState(null);

  const currencyPairs = ['MAD/EUR', 'MAD/USD'];

  useEffect(() => {
    fetchLatestRates();
  }, []);

  useEffect(() => {
    fetchPredictions();
  }, [selectedPair, daysHistory]);

  const fetchLatestRates = async () => {
    try {
      const response = await publicAPI.getLatestExchangeRates();
      setLatestRates(response.data.data);
    } catch (error) {
      console.error('Error fetching latest rates:', error);
    }
  };

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await publicAPI.getExchangePredictions(selectedPair, daysHistory, 7);
      const data = response.data.data;

      // Combiner les données historiques et prédictions
      const combined = [
        ...(data.historical || []).map(item => ({
          date: item.date,
          achat: item.achat,
          vente: item.vente,
          moyenne: item.moyenne,
          type: 'actual'
        })),
        ...(data.predictions || []).map(item => ({
          date: item.date,
          predicted_moyenne: item.predicted_moyenne,
          confidence_score: item.confidence_score,
          type: 'predicted'
        }))
      ];

      setChartData(combined);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      if (error.response?.status === 404) {
        setError('Aucune prédiction disponible. Le modèle doit être entraîné.');
      } else {
        setError('Erreur lors du chargement des données');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isPrediction = data.type === 'predicted';

      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-semibold text-gray-800">{formatDate(label)}</p>
          {isPrediction ? (
            <>
              <p className="text-purple-600">
                Prédiction: {data.predicted_moyenne?.toFixed(4)}
              </p>
              {data.confidence_score && (
                <p className="text-sm text-gray-600">
                  Confiance: {(data.confidence_score * 100).toFixed(0)}%
                </p>
              )}
            </>
          ) : (
            <>
              <p className="text-green-600">Achat: {data.achat?.toFixed(4)}</p>
              <p className="text-red-600">Vente: {data.vente?.toFixed(4)}</p>
              <p className="text-blue-600">Moyenne: {data.moyenne?.toFixed(4)}</p>
            </>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            Taux de Change MAD
          </h1>

          {/* Latest Rates Cards */}
          {latestRates && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* MAD/EUR Card */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                <h2 className="text-xl font-semibold text-gray-700 mb-3">
                  MAD/EUR
                </h2>
                {latestRates['MAD/EUR'] ? (
                  <>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Achat:</span>
                        <span className="text-2xl font-bold text-green-600">
                          {latestRates['MAD/EUR'].achat?.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Vente:</span>
                        <span className="text-2xl font-bold text-red-600">
                          {latestRates['MAD/EUR'].vente?.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Moyenne:</span>
                        <span className="text-xl font-semibold text-blue-600">
                          {latestRates['MAD/EUR'].moyenne?.toFixed(4)}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-3">
                      Date: {new Date(latestRates['MAD/EUR'].date).toLocaleDateString('fr-FR')}
                    </p>
                  </>
                ) : (
                  <p className="text-gray-500">Données non disponibles</p>
                )}
              </div>

              {/* MAD/USD Card */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                <h2 className="text-xl font-semibold text-gray-700 mb-3">
                  MAD/USD
                </h2>
                {latestRates['MAD/USD'] ? (
                  <>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Achat:</span>
                        <span className="text-2xl font-bold text-green-600">
                          {latestRates['MAD/USD'].achat?.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Vente:</span>
                        <span className="text-2xl font-bold text-red-600">
                          {latestRates['MAD/USD'].vente?.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Moyenne:</span>
                        <span className="text-xl font-semibold text-blue-600">
                          {latestRates['MAD/USD'].moyenne?.toFixed(4)}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-3">
                      Date: {new Date(latestRates['MAD/USD'].date).toLocaleDateString('fr-FR')}
                    </p>
                  </>
                ) : (
                  <p className="text-gray-500">Données non disponibles</p>
                )}
              </div>
            </div>
          )}

          {/* Chart Controls */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Historique et Prédictions
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Paire de devises
                </label>
                <select
                  value={selectedPair}
                  onChange={(e) => setSelectedPair(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {currencyPairs.map(pair => (
                    <option key={pair} value={pair}>{pair}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Période d'historique (jours)
                </label>
                <select
                  value={daysHistory}
                  onChange={(e) => setDaysHistory(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={7}>7 jours</option>
                  <option value={14}>14 jours</option>
                  <option value={30}>30 jours</option>
                  <option value={60}>60 jours</option>
                  <option value={90}>90 jours</option>
                  <option value={180}>6 mois</option>
                  <option value={365}>1 an</option>
                </select>
              </div>
            </div>
          </div>

          {/* Chart */}
          {loading ? (
            <div className="flex justify-center items-center h-96">
              <div className="text-xl text-gray-500">Chargement...</div>
            </div>
          ) : error ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <p className="text-yellow-800">{error}</p>
            </div>
          ) : chartData.length > 0 ? (
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    domain={['auto', 'auto']}
                    tickFormatter={(value) => value.toFixed(4)}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />

                  {/* Ligne pour les données historiques */}
                  <Line
                    type="monotone"
                    dataKey="moyenne"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    name="Taux actuel"
                    dot={{ r: 2 }}
                    connectNulls
                  />

                  {/* Ligne pour les prédictions */}
                  <Line
                    type="monotone"
                    dataKey="predicted_moyenne"
                    stroke="#A855F7"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Prédictions ML"
                    dot={{ r: 4, fill: '#A855F7' }}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>

              {/* Legend */}
              <div className="mt-4 flex justify-center space-x-6 text-sm">
                <div className="flex items-center">
                  <div className="w-8 h-0.5 bg-blue-500 mr-2"></div>
                  <span className="text-gray-600">Taux réels</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-0.5 bg-purple-500 mr-2 border-t-2 border-dashed"></div>
                  <span className="text-gray-600">Prédictions ML (7 jours)</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-500">Aucune donnée disponible</p>
            </div>
          )}

          {/* Info Box */}
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">ℹ️ À propos des prédictions</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Les prédictions sont générées par un modèle LSTM entraîné sur l'historique des taux</li>
              <li>• Le modèle utilise 30 jours d'historique pour prédire les 7 prochains jours</li>
              <li>• Les prédictions sont mises à jour quotidiennement</li>
              <li>• Les données sont fournies par Bank Al-Maghrib</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default ExchangeRates;
