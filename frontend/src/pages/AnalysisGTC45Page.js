import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AnalysisGTC45Page() {
  const { matrizId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [matriz, setMatriz] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMatriz();
  }, [matrizId]);

  const fetchMatriz = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/gtc45/matriz/${matrizId}`);
      setMatriz(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar la matriz');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get(`${API}/gtc45/download/${matrizId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `matriz_gtc45_${matrizId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Error al descargar el archivo');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#002FA7] animate-spin mx-auto mb-4" strokeWidth={1.5} />
          <p className="text-sm uppercase tracking-widest font-semibold text-[#002FA7]">CARGANDO MATRIZ GTC 45...</p>
        </div>
      </div>
    );
  }

  if (error || !matriz) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="max-w-md w-full bg-white border-2 border-[#DC2626] p-8">
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>ERROR</h2>
          <p className="text-sm text-[#52525B] mb-6">{error || 'Matriz no encontrada'}</p>
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

  const getRiskColor = (interpretacion) => {
    const colors = {
      'I': '#DC2626',
      'II': '#EA580C',
      'III': '#EAB308',
      'IV': '#16A34A'
    };
    return colors[interpretacion] || '#71717A';
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
          <button
            onClick={() => navigate('/')}
            className="text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} /> VOLVER
          </button>
          
          <button
            onClick={handleDownload}
            className="bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-3 px-6 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" strokeWidth={1.5} /> DESCARGAR EXCEL GTC 45
          </button>
        </div>

        <header className="mb-12 bg-white border-2 border-[#E4E4E7] p-8">
          <h1 className="text-4xl sm:text-5xl font-black mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            MATRIZ GTC 45:2012
          </h1>
          <p className="text-base text-[#52525B] mb-6">{matriz.nombre_empresa} - {matriz.documento_origen}</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#DC2626] text-white p-4">
              <p className="text-xs uppercase tracking-wider mb-1">CRÍTICOS</p>
              <p className="text-3xl font-black">{matriz.estadisticas.criticos}</p>
            </div>
            <div className="bg-[#EA580C] text-white p-4">
              <p className="text-xs uppercase tracking-wider mb-1">ALTOS</p>
              <p className="text-3xl font-black">{matriz.estadisticas.altos}</p>
            </div>
            <div className="bg-[#EAB308] text-black p-4">
              <p className="text-xs uppercase tracking-wider mb-1">MEDIOS</p>
              <p className="text-3xl font-black">{matriz.estadisticas.medios}</p>
            </div>
            <div className="bg-[#16A34A] text-white p-4">
              <p className="text-xs uppercase tracking-wider mb-1">BAJOS</p>
              <p className="text-3xl font-black">{matriz.estadisticas.bajos}</p>
            </div>
          </div>
        </header>

        <div className="bg-white border-2 border-[#E4E4E7] p-8 mb-12">
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>RESUMEN EJECUTIVO</h2>
          <p className="text-base leading-relaxed text-[#52525B]">{matriz.resumen_ejecutivo}</p>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>RIESGOS IDENTIFICADOS ({matriz.estadisticas.total_riesgos})</h2>
        </div>

        <div className="space-y-4">
          {matriz.riesgos.map((riesgo, index) => (
            <div key={riesgo.id} className="bg-white border-2 border-[#E4E4E7] p-6 hover:border-[#0A0A0A] transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold mb-1" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                    {riesgo.proceso.nombre} → {riesgo.actividad.nombre}
                  </h3>
                  <p className="text-sm text-[#71717A]">{riesgo.tarea.nombre}</p>
                </div>
                <div
                  className="px-4 py-2 text-white font-bold text-sm uppercase"
                  style={{ backgroundColor: getRiskColor(riesgo.valoracion.interpretacion) }}
                >
                  NIVEL {riesgo.valoracion.interpretacion}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-semibold text-[#09090B] mb-1">Peligro:</p>
                  <p className="text-[#52525B]">{riesgo.peligro.clasificacion} - {riesgo.peligro.descripcion}</p>
                </div>
                <div>
                  <p className="font-semibold text-[#09090B] mb-1">Valoración:</p>
                  <p className="text-[#52525B] font-mono">NR={riesgo.valoracion.nr_valor} (NP={riesgo.valoracion.np_valor} × NC={riesgo.valoracion.nc_valor})</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
