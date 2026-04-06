import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, ArrowLeft, AlertTriangle, Loader2, Shield, Scale } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/v1`;

export default function AnalysisPage() {
  const { matrizId } = useParams();
  const navigate = useNavigate();
  const [matriz, setMatriz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchMatriz();
  }, [matrizId]);

  const fetchMatriz = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/matrix/${matrizId}`);
      setMatriz(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar la matriz');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      setDownloading(true);
      const response = await axios.get(`${API}/matrix/${matrizId}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `matriz_sst_${matriz.empresa.replace(/\s+/g, '_')}_${matrizId.substring(0, 8)}.xlsx`;
      link.setAttribute('download', filename);
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
      'Bajo': 'bg-[#16A34A] text-white',
      'Trivial': 'bg-[#A1A1AA] text-white'
    };
    return colors[nivel] || 'bg-[#A1A1AA] text-white';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#002FA7] animate-spin mx-auto mb-4" strokeWidth={1.5} />
          <p className="text-sm uppercase tracking-widest font-semibold text-[#002FA7]">CARGANDO MATRIZ...</p>
        </div>
      </div>
    );
  }

  if (error || !matriz) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="max-w-md w-full bg-white border-2 border-[#DC2626] p-8">
          <AlertTriangle className="w-12 h-12 text-[#DC2626] mb-4" strokeWidth={1.5} />
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

          <button
            data-testid="download-button"
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-3 px-6 transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" strokeWidth={2} />
            {downloading ? 'DESCARGANDO...' : 'DESCARGAR EXCEL'}
          </button>
        </div>

        {/* TÍTULO Y STATS */}
        <div className="mb-12 bg-white border-2 border-[#E4E4E7] p-8">
          <div className="flex items-start gap-4 mb-6">
            <Shield className="w-10 h-10 text-[#002FA7]" />
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl sm:text-4xl tracking-tighter font-black" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                  MATRIZ SST (GTC 45)
                </h1>
              </div>
              <p className="text-base text-[#52525B]">
                <span className="font-semibold">{matriz.empresa}</span> • {matriz.documento_origen}
              </p>
              <p className="text-sm text-[#71717A] mt-1">
                Generado: {new Date(matriz.created_at).toLocaleDateString('es-ES')} • {matriz.metodologia}
              </p>
            </div>
          </div>

          {/* ESTADÍSTICAS */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="bg-[#FAFAFA] border-2 border-[#E4E4E7] p-4">
              <p className="text-xs uppercase tracking-wider text-[#71717A] mb-1">Total</p>
              <p className="text-2xl font-bold">{matriz.total_riesgos}</p>
            </div>
            <div className="bg-[#DC2626] border-2 border-[#DC2626] p-4 text-white">
              <p className="text-xs uppercase tracking-wider mb-1">Críticos</p>
              <p className="text-2xl font-bold">{matriz.riesgos_criticos}</p>
            </div>
            <div className="bg-[#EA580C] border-2 border-[#EA580C] p-4 text-white">
              <p className="text-xs uppercase tracking-wider mb-1">Altos</p>
              <p className="text-2xl font-bold">{matriz.riesgos_altos}</p>
            </div>
            <div className="bg-[#EAB308] border-2 border-[#EAB308] p-4">
              <p className="text-xs uppercase tracking-wider mb-1">Medios</p>
              <p className="text-2xl font-bold">{matriz.riesgos_medios}</p>
            </div>
            <div className="bg-[#16A34A] border-2 border-[#16A34A] p-4 text-white">
              <p className="text-xs uppercase tracking-wider mb-1">Bajos</p>
              <p className="text-2xl font-bold">{matriz.riesgos_bajos}</p>
            </div>
          </div>
        </div>

        {/* MENSAJE DE ÉXITO */}
        <div className="mb-8 bg-[#F0FDF4] border-2 border-[#16A34A] p-6 flex items-start gap-4">
          <div className="w-8 h-8 bg-[#16A34A] flex items-center justify-center">
            <Download className="w-5 h-5 text-white" strokeWidth={2} />
          </div>
          <div className="flex-1">
            <h3 className="font-bold mb-2 uppercase tracking-wider text-sm">MATRIZ GENERADA EXITOSAMENTE</h3>
            <p className="text-sm text-[#52525B]">
              Tu matriz de riesgos ha sido generada con {matriz.total_riesgos} riesgos identificados. 
              Haz clic en "DESCARGAR EXCEL" para obtener el archivo completo con:
            </p>
            <ul className="mt-3 space-y-1 text-sm text-[#52525B]">
              <li>• Identificación completa de riesgos</li>
              <li>• Evaluación según metodología {matriz.metodologia}</li>
              <li>• Controles existentes y propuestos</li>
              <li>• Fuentes de información documentadas</li>
              <li>• Clasificación por nivel de riesgo con colores</li>
            </ul>
          </div>
        </div>

        {/* VISTA PREVIA */}
        <div className="bg-white border-2 border-[#E4E4E7] p-8">
          <h2 className="text-2xl font-bold mb-6 uppercase tracking-wider" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            VISTA PREVIA DE LA MATRIZ
          </h2>
          <p className="text-sm text-[#52525B] mb-6">
            La matriz completa con todos los detalles está disponible en el archivo Excel. 
            Para visualizar y editar la matriz, descarga el archivo usando el botón superior.
          </p>

          <div className="bg-[#FAFAFA] border-2 border-[#E4E4E7] p-8 text-center">
            <Shield className="w-16 h-16 text-[#A1A1AA] mx-auto mb-4" />
            <p className="text-sm text-[#71717A] mb-4">
              Archivo Excel generado con {matriz.total_riesgos} filas de datos
            </p>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="bg-[#002FA7] text-white hover:bg-[#002685] font-semibold uppercase tracking-widest text-sm py-3 px-8 transition-colors disabled:opacity-50"
            >
              {downloading ? 'DESCARGANDO...' : 'DESCARGAR ARCHIVO'}
            </button>
          </div>
        </div>

        {/* INFORMACIÓN ADICIONAL */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border-2 border-[#E4E4E7] p-6">
            <div className="text-[#002FA7] text-xl font-bold mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>01</div>
            <h4 className="font-semibold mb-2 text-sm uppercase tracking-wider">METODOLOGÍA UTILIZADA</h4>
            <p className="text-sm text-[#52525B]">{matriz.metodologia}</p>
          </div>

          <div className="bg-white border-2 border-[#E4E4E7] p-6">
            <div className="text-[#002FA7] text-xl font-bold mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>02</div>
            <h4 className="font-semibold mb-2 text-sm uppercase tracking-wider">DOCUMENTO ANALIZADO</h4>
            <p className="text-sm text-[#52525B]">{matriz.documento_origen}</p>
          </div>

          <div className="bg-white border-2 border-[#E4E4E7] p-6">
            <div className="text-[#002FA7] text-xl font-bold mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>03</div>
            <h4 className="font-semibold mb-2 text-sm uppercase tracking-wider">FORMATO DE EXPORTACIÓN</h4>
            <p className="text-sm text-[#52525B]">Excel (.xlsx) con formato GTC 45 profesional y colores por nivel de riesgo</p>
          </div>
        </div>
      </div>
    </div>
  );
}
