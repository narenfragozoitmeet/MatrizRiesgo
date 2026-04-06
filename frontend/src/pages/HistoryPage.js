import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, Loader2, Shield, Scale, Download } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/v1`;

export default function HistoryPage() {
  const navigate = useNavigate();
  const [matrices, setMatrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'sst', 'legal'

  useEffect(() => {
    fetchMatrices();
  }, []);

  const fetchMatrices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/matrices`);
      setMatrices(response.data);
    } catch (err) {
      console.error('Error fetching matrices:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (count) => {
    if (count >= 5) return 'text-[#DC2626]';
    if (count >= 2) return 'text-[#EA580C]';
    if (count >= 1) return 'text-[#EAB308]';
    return 'text-[#16A34A]';
  };

  const filteredMatrices = matrices.filter(m => {
    if (filter === 'all') return true;
    return m.tipo_matriz === filter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#002FA7] animate-spin mx-auto mb-4" strokeWidth={1.5} />
          <p className="text-sm uppercase tracking-widest font-semibold text-[#002FA7]">CARGANDO HISTORIAL...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        {/* HEADER */}
        <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
          <button
            data-testid="back-button"
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={2} />
            VOLVER
          </button>
        </div>

        {/* TÍTULO */}
        <div className="mb-8">
          <h1 className="text-4xl sm:text-5xl tracking-tighter font-black mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            HISTORIAL DE MATRICES
          </h1>
          <p className="text-base text-[#52525B]">
            Accede a todas las matrices de riesgos generadas previamente
          </p>
        </div>

        {/* FILTROS */}
        <div className="mb-8 flex gap-3 flex-wrap">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 text-sm font-bold uppercase tracking-wider transition-all ${
              filter === 'all'
                ? 'bg-[#0A0A0A] text-white'
                : 'bg-white border-2 border-[#E4E4E7] hover:border-[#0A0A0A]'
            }`}
          >
            Todas ({matrices.length})
          </button>
          <button
            onClick={() => setFilter('sst')}
            className={`px-4 py-2 text-sm font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
              filter === 'sst'
                ? 'bg-[#002FA7] text-white'
                : 'bg-white border-2 border-[#E4E4E7] hover:border-[#002FA7]'
            }`}
          >
            <Shield className="w-4 h-4" />
            SST ({matrices.filter(m => m.tipo_matriz === 'sst').length})
          </button>
          <button
            onClick={() => setFilter('legal')}
            className={`px-4 py-2 text-sm font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
              filter === 'legal'
                ? 'bg-[#002FA7] text-white'
                : 'bg-white border-2 border-[#E4E4E7] hover:border-[#002FA7]'
            }`}
          >
            <Scale className="w-4 h-4" />
            Legal ({matrices.filter(m => m.tipo_matriz === 'legal').length})
          </button>
        </div>

        {/* LISTADO */}
        {filteredMatrices.length === 0 ? (
          <div className="bg-white border-2 border-[#E4E4E7] p-12 text-center">
            <FileText className="w-16 h-16 text-[#A1A1AA] mx-auto mb-4" strokeWidth={1.5} />
            <h3 className="text-xl font-bold mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              NO HAY MATRICES
            </h3>
            <p className="text-sm text-[#71717A] mb-6">
              {filter === 'all' 
                ? 'Aún no has generado ninguna matriz de riesgos'
                : `No hay matrices de tipo ${filter.toUpperCase()}`
              }
            </p>
            <button
              onClick={() => navigate('/')}
              className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-3 px-6 transition-colors"
            >
              GENERAR PRIMERA MATRIZ
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredMatrices.map((matriz) => {
              const TipoIcon = matriz.tipo_matriz === 'sst' ? Shield : Scale;
              const tipoLabel = matriz.tipo_matriz === 'sst' ? 'SST' : 'LEGAL';
              const tipoColor = matriz.tipo_matriz === 'sst' ? 'text-[#002FA7]' : 'text-[#0A0A0A]';
              
              return (
                <div
                  key={matriz.id}
                  data-testid="matrix-card"
                  className="bg-white border-2 border-[#E4E4E7] p-6 transition-all hover:border-[#0A0A0A] hover:shadow-brutal cursor-pointer"
                  onClick={() => navigate(`/analysis/${matriz.tipo_matriz}/${matriz.id}`)}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 border-2 border-[#E4E4E7] flex items-center justify-center ${tipoColor}`}>
                      <TipoIcon className="w-6 h-6" strokeWidth={1.5} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 ${
                              matriz.tipo_matriz === 'sst' 
                                ? 'bg-[#F0F4FF] text-[#002FA7]' 
                                : 'bg-[#FAFAFA] text-[#0A0A0A]'
                            }`}>
                              {tipoLabel}
                            </span>
                            <h3 className="text-lg font-bold truncate" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                              {matriz.empresa}
                            </h3>
                          </div>
                          <p className="text-sm text-[#71717A]">
                            {matriz.documento_origen}
                          </p>
                          <p className="text-xs text-[#A1A1AA] mt-1">
                            {new Date(matriz.created_at).toLocaleDateString('es-ES', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </p>
                        </div>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            window.open(`${API}/matrix/${matriz.tipo_matriz}/${matriz.id}/export`, '_blank');
                          }}
                          className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] p-2 transition-colors"
                          title="Descargar Excel"
                        >
                          <Download className="w-4 h-4" strokeWidth={2} />
                        </button>
                      </div>
                      
                      {/* STATS */}
                      <div className="mt-4 flex items-center gap-6 flex-wrap">
                        <div className="flex items-center gap-2">
                          <span className="text-xs uppercase tracking-wider text-[#71717A]">Total:</span>
                          <span className="text-sm font-bold">{matriz.total_riesgos}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs uppercase tracking-wider text-[#71717A]">Críticos:</span>
                          <span className={`text-sm font-bold ${getRiskColor(matriz.riesgos_criticos)}`}>
                            {matriz.riesgos_criticos}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs uppercase tracking-wider text-[#71717A]">Altos:</span>
                          <span className={`text-sm font-bold ${getRiskColor(matriz.riesgos_altos)}`}>
                            {matriz.riesgos_altos}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs uppercase tracking-wider text-[#71717A]">Medios:</span>
                          <span className="text-sm font-bold text-[#EAB308]">{matriz.riesgos_medios}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs uppercase tracking-wider text-[#71717A]">Bajos:</span>
                          <span className="text-sm font-bold text-[#16A34A]">{matriz.riesgos_bajos}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
