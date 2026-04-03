import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, ArrowLeft, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AnalysisPage() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchAnalysis();
  }, [analysisId]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/analysis/${analysisId}`);
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar el análisis');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      setDownloading(true);
      const response = await axios.get(`${API}/download/${analysisId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `matriz_riesgos_${analysis.document_name.replace(/\.[^/.]+$/, '')}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Error al descargar el archivo');
    } finally {
      setDownloading(false);
    }
  };

  const getRiskColor = (nivel) => {
    const colors = {
      'Crítico': 'bg-[#DC2626] text-white',
      'Alto': 'bg-[#EA580C] text-white',
      'Medio': 'bg-[#EAB308] text-black',
      'Bajo': 'bg-[#16A34A] text-white'
    };
    return colors[nivel] || 'bg-[#A1A1AA] text-white';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#002FA7] animate-spin mx-auto mb-4" strokeWidth={1.5} />
          <p className="text-sm uppercase tracking-widest font-semibold text-[#002FA7]">CARGANDO ANÁLISIS...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="max-w-md w-full bg-white border-2 border-[#DC2626] p-8">
          <AlertTriangle className="w-12 h-12 text-[#DC2626] mb-4" strokeWidth={1.5} />
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>ERROR</h2>
          <p className="text-sm text-[#52525B] mb-6">{error || 'Análisis no encontrado'}</p>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-4 px-8 transition-colors"
          >
            VOLVER AL INICIO
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
          <button
            data-testid="back-button"
            onClick={() => navigate('/')}
            className="text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} /> VOLVER
          </button>
          
          <button
            data-testid="download-excel-button"
            onClick={handleDownload}
            disabled={downloading}
            className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-3 px-6 transition-colors border border-transparent hover:border-[#002FA7] flex items-center gap-2 disabled:opacity-50"
          >
            <Download className="w-4 h-4" strokeWidth={1.5} />
            {downloading ? 'DESCARGANDO...' : 'DESCARGAR EXCEL'}
          </button>
        </div>

        <header className="mb-12 bg-white border-2 border-[#E4E4E7] p-8">
          <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
            <div>
              <h1 className="text-4xl sm:text-5xl font-black mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                ANÁLISIS COMPLETADO
              </h1>
              <p className="text-base text-[#52525B]">{analysis.document_name}</p>
            </div>
            <div className="bg-[#16A34A] text-white px-4 py-2 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
              <CheckCircle className="w-4 h-4" strokeWidth={1.5} />
              {analysis.status === 'completed' ? 'COMPLETADO' : analysis.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#FAFAFA] p-4 border-2 border-[#E4E4E7]">
              <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">TOTAL RIESGOS</p>
              <p className="text-3xl font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{analysis.total_risks}</p>
            </div>
            
            <div className="bg-[#FAFAFA] p-4 border-2 border-[#E4E4E7]">
              <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">FECHA ANÁLISIS</p>
              <p className="text-sm font-semibold">{new Date(analysis.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>
            
            <div className="bg-[#FAFAFA] p-4 border-2 border-[#E4E4E7]">
              <p className="text-xs uppercase tracking-[0.2em] font-medium text-[#71717A] mb-2">DOCUMENTO</p>
              <p className="text-sm font-semibold truncate">{analysis.document_name}</p>
            </div>
          </div>
        </header>

        <div className="mb-12 bg-white border-2 border-[#E4E4E7] p-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>RESUMEN EJECUTIVO</h2>
          <p className="text-base leading-relaxed text-[#52525B]">{analysis.summary}</p>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>MATRIZ DE RIESGOS</h2>
        </div>

        <div className="overflow-x-auto">
          <table data-testid="risk-matrix-table" className="w-full border-collapse text-left bg-white border-2 border-[#E4E4E7]">
            <thead>
              <tr className="bg-[#0A0A0A] border-b-2 border-[#0A0A0A]">
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Categoría</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Riesgo</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Descripción</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Probabilidad</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Impacto</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Nivel</th>
                <th className="p-4 text-white font-semibold text-sm uppercase tracking-wider">Mitigación</th>
              </tr>
            </thead>
            <tbody>
              {analysis.risks.map((risk, index) => (
                <tr key={index} className="border-b border-[#E4E4E7] hover:bg-[#FAFAFA] transition-colors" data-testid={`risk-row-${index}`}>
                  <td className="p-4 text-sm text-[#52525B] font-semibold">{risk.categoria}</td>
                  <td className="p-4 text-sm text-[#09090B] font-semibold">{risk.riesgo}</td>
                  <td className="p-4 text-sm text-[#52525B]">{risk.descripcion}</td>
                  <td className="p-4 text-sm text-[#52525B]">{risk.probabilidad}</td>
                  <td className="p-4 text-sm text-[#52525B]">{risk.impacto}</td>
                  <td className="p-4">
                    <span className={`px-3 py-1 text-xs font-bold uppercase tracking-wider ${getRiskColor(risk.nivel_riesgo)}`}>
                      {risk.nivel_riesgo}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-[#52525B]">{risk.mitigacion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-12 text-center">
          <button
            data-testid="download-excel-button-bottom"
            onClick={handleDownload}
            disabled={downloading}
            className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-4 px-8 transition-colors border border-transparent hover:border-[#002FA7] inline-flex items-center gap-2 disabled:opacity-50 shadow-brutal hover:shadow-brutal-sm"
          >
            <Download className="w-5 h-5" strokeWidth={1.5} />
            {downloading ? 'DESCARGANDO...' : 'DESCARGAR MATRIZ EN EXCEL'}
          </button>
        </div>
      </div>
    </div>
  );
}