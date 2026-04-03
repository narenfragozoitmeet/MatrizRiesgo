import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, BarChart3, TrendingUp, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/gtc45/dashboard/stats`);
      setStats(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#002FA7] animate-spin mx-auto mb-4" strokeWidth={1.5} />
          <p className="text-sm uppercase tracking-widest font-semibold text-[#002FA7]">CARGANDO DASHBOARD...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors flex items-center gap-2 mb-8"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} /> VOLVER AL INICIO
          </button>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl tracking-tighter font-black mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            DASHBOARD SST
          </h1>
          <p className="text-base leading-relaxed text-[#52525B]">
            Métricas y tendencias de análisis de riesgos GTC 45:2012
          </p>
        </div>

        {error ? (
          <div className="bg-white border-2 border-[#DC2626] p-8">
            <p className="text-[#DC2626]">{error}</p>
          </div>
        ) : stats ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <div className="bg-white border-2 border-[#E4E4E7] p-6 hover:border-[#0A0A0A] hover:shadow-brutal transition-all">
                <BarChart3 className="w-8 h-8 text-[#002FA7] mb-3" strokeWidth={1.5} />
                <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">MATRICES</p>
                <p className="text-4xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{stats.total_matrices}</p>
              </div>

              <div className="bg-white border-2 border-[#E4E4E7] p-6 hover:border-[#0A0A0A] hover:shadow-brutal transition-all">
                <TrendingUp className="w-8 h-8 text-[#002FA7] mb-3" strokeWidth={1.5} />
                <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">RIESGOS TOTALES</p>
                <p className="text-4xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{stats.total_riesgos}</p>
              </div>

              <div className="bg-white border-2 border-[#E4E4E7] p-6 hover:border-[#0A0A0A] hover:shadow-brutal transition-all">
                <AlertTriangle className="w-8 h-8 text-[#DC2626] mb-3" strokeWidth={1.5} />
                <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">NIVEL MÁS FRECUENTE</p>
                <p className="text-4xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{stats.nivel_mas_frecuente}</p>
              </div>

              <div className="bg-white border-2 border-[#E4E4E7] p-6 hover:border-[#0A0A0A] hover:shadow-brutal transition-all">
                <CheckCircle2 className="w-8 h-8 text-[#16A34A] mb-3" strokeWidth={1.5} />
                <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">TASA CRÍTICOS</p>
                <p className="text-4xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                  {stats.total_riesgos > 0 ? Math.round((stats.por_nivel.criticos / stats.total_riesgos) * 100) : 0}%
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white border-2 border-[#E4E4E7] p-8">
                <h2 className="text-2xl font-bold mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>DISTRIBUCIÓN POR NIVEL</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">Nivel I (Crítico)</span>
                    <div className="flex items-center gap-3">
                      <div className="bg-[#DC2626] h-8 flex items-center justify-center px-4 text-white font-bold text-sm">
                        {stats.por_nivel.criticos}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">Nivel II (Alto)</span>
                    <div className="flex items-center gap-3">
                      <div className="bg-[#EA580C] h-8 flex items-center justify-center px-4 text-white font-bold text-sm">
                        {stats.por_nivel.altos}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">Nivel III (Medio)</span>
                    <div className="flex items-center gap-3">
                      <div className="bg-[#EAB308] h-8 flex items-center justify-center px-4 text-black font-bold text-sm">
                        {stats.por_nivel.medios}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">Nivel IV (Bajo)</span>
                    <div className="flex items-center gap-3">
                      <div className="bg-[#16A34A] h-8 flex items-center justify-center px-4 text-white font-bold text-sm">
                        {stats.por_nivel.bajos}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white border-2 border-[#E4E4E7] p-8">
                <h2 className="text-2xl font-bold mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>PELIGROS POR CLASIFICACIÓN</h2>
                <div className="space-y-3">
                  {Object.entries(stats.por_clasificacion || {}).map(([clasificacion, cantidad]) => (
                    <div key={clasificacion} className="flex items-center justify-between">
                      <span className="text-sm text-[#52525B]">{clasificacion}</span>
                      <span className="text-lg font-bold" style={{ fontFamily: 'JetBrains Mono, monospace' }}>{cantidad}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
