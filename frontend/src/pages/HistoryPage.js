import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, Clock, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HistoryPage() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/analyses`);
      setAnalyses(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar el historial');
    } finally {
      setLoading(false);
    }
  };

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
        <div className="mb-8">
          <button
            data-testid="back-to-home-button"
            onClick={() => navigate('/')}
            className="text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors flex items-center gap-2 mb-8"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} /> VOLVER AL INICIO
          </button>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl tracking-tighter font-black mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            HISTORIAL DE ANÁLISIS
          </h1>
          <p className="text-base leading-relaxed text-[#52525B]">
            Revisa todos los análisis de riesgos legales realizados.
          </p>
        </div>

        {error && (
          <div className="mb-8 bg-white border-2 border-[#DC2626] p-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-[#DC2626] mt-0.5" strokeWidth={1.5} />
            <p className="text-sm font-medium text-[#DC2626]">{error}</p>
          </div>
        )}

        {analyses.length === 0 && !error ? (
          <div className="bg-white border-2 border-[#E4E4E7] p-12 text-center">
            <FileText className="w-16 h-16 text-[#A1A1AA] mx-auto mb-6" strokeWidth={1.5} />
            <h3 className="text-xl font-bold mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>NO HAY ANÁLISIS REALIZADOS</h3>
            <p className="text-sm text-[#52525B] mb-6">Sube tu primer documento para comenzar.</p>
            <button
              onClick={() => navigate('/')}
              className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-3 px-6 transition-colors inline-block"
            >
              SUBIR DOCUMENTO
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                data-testid={`analysis-card-${analysis.id}`}
                onClick={() => navigate(`/analysis/${analysis.id}`)}
                className="bg-white border-2 border-[#E4E4E7] p-6 transition-all hover:border-[#0A0A0A] hover:shadow-brutal cursor-pointer"
              >
                <div className="flex items-start gap-3 mb-4">
                  <FileText className="w-6 h-6 text-[#002FA7] mt-1" strokeWidth={1.5} />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-bold text-[#09090B] mb-1 truncate" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                      {analysis.document_name}
                    </h3>
                    <p className="text-xs text-[#71717A] flex items-center gap-1">
                      <Clock className="w-3 h-3" strokeWidth={1.5} />
                      {new Date(analysis.created_at).toLocaleDateString('es-ES', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-1">RIESGOS</p>
                    <p className="text-2xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{analysis.total_risks}</p>
                  </div>
                  
                  <div className="bg-[#16A34A] text-white px-3 py-1 text-xs font-bold uppercase tracking-wider">
                    {analysis.status === 'completed' ? 'OK' : analysis.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}