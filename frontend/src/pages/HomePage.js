import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HomePage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState('');

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError('');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    setError('');
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ];
    
    if (!validTypes.includes(selectedFile.type)) {
      setError('Tipo de archivo no soportado. Use PDF, Word (.docx) o Excel (.xlsx)');
      return;
    }
    
    setFile(selectedFile);
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) return;
    
    try {
      setUploading(true);
      setError('');
      setProgress('Subiendo documento...');
      
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadResponse = await axios.post(`${API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const documentId = uploadResponse.data.id;
      setUploading(false);
      setAnalyzing(true);
      setProgress('Analizando documento con IA...');
      
      const analysisResponse = await axios.post(`${API}/analyze/${documentId}`);
      
      setAnalyzing(false);
      navigate(`/analysis/${analysisResponse.data.id}`);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el documento');
      setUploading(false);
      setAnalyzing(false);
      setProgress('');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        <header className="mb-12">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl tracking-tighter font-black mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            MATRIZ DE RIESGOS LEGALES
          </h1>
          <p className="text-base leading-relaxed text-[#52525B] max-w-2xl">
            Sube documentos de tu empresa y obtén una matriz de riesgos legales estructurada automáticamente mediante inteligencia artificial.
          </p>
          <button
            data-testid="history-button"
            onClick={() => navigate('/history')}
            className="mt-6 text-sm uppercase tracking-widest font-semibold text-[#002FA7] hover:text-[#002685] transition-colors"
          >
            VER HISTORIAL →
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            data-testid="upload-zone"
            className={`border-2 border-dashed bg-[#FAFAFA] p-16 text-center cursor-pointer min-h-[400px] flex flex-col items-center justify-center transition-all ${
              dragActive
                ? 'border-[#002FA7] bg-[#F0F4FF]'
                : 'border-[#E4E4E7] hover:border-[#002FA7] hover:bg-[#F0F4FF]'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <Upload className="w-16 h-16 text-[#002FA7] mb-6" strokeWidth={1.5} />
            <h3 className="text-xl sm:text-2xl font-bold mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              ARRASTRA TU DOCUMENTO AQUÍ
            </h3>
            <p className="text-sm uppercase tracking-[0.2em] font-medium text-[#71717A] mb-6">
              O HAZ CLIC PARA SELECCIONAR
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <span className="bg-[#DC2626] text-white px-3 py-1 text-xs font-bold uppercase tracking-wider">PDF</span>
              <span className="bg-[#002FA7] text-white px-3 py-1 text-xs font-bold uppercase tracking-wider">WORD</span>
              <span className="bg-[#16A34A] text-white px-3 py-1 text-xs font-bold uppercase tracking-wider">EXCEL</span>
            </div>
            <input
              id="fileInput"
              data-testid="file-input"
              type="file"
              onChange={handleChange}
              accept=".pdf,.doc,.docx,.xls,.xlsx"
              className="hidden"
            />
          </div>

          <div className="bg-white border-2 border-[#E4E4E7] p-8 transition-all hover:border-[#0A0A0A] hover:shadow-brutal">
            <h3 className="text-xl sm:text-2xl font-bold mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              ESTADO DEL PROCESO
            </h3>
            
            {file && (
              <div data-testid="selected-file" className="mb-6 p-4 bg-[#FAFAFA] border-2 border-[#E4E4E7] flex items-start gap-3">
                <FileText className="w-5 h-5 text-[#002FA7] mt-1" strokeWidth={1.5} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-[#09090B] truncate">{file.name}</p>
                  <p className="text-xs text-[#71717A] mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                </div>
              </div>
            )}

            {error && (
              <div data-testid="error-message" className="mb-6 p-4 bg-[#DC2626] text-white flex items-start gap-3">
                <AlertCircle className="w-5 h-5 mt-0.5" strokeWidth={1.5} />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}

            {progress && (
              <div data-testid="progress-message" className="mb-6 p-4 bg-[#F0F4FF] border-2 border-[#002FA7]">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 text-[#002FA7] animate-spin" strokeWidth={1.5} />
                  <p className="text-sm font-semibold text-[#002FA7] uppercase tracking-wider">{progress}</p>
                </div>
              </div>
            )}

            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <div className={`w-6 h-6 border-2 flex items-center justify-center text-xs font-bold ${
                  file ? 'bg-[#002FA7] border-[#002FA7] text-white' : 'border-[#E4E4E7] text-[#A1A1AA]'
                }`}>
                  1
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#09090B]">Cargar Documento</p>
                  <p className="text-xs text-[#71717A] mt-1">PDF, Word o Excel</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className={`w-6 h-6 border-2 flex items-center justify-center text-xs font-bold ${
                  analyzing ? 'bg-[#002FA7] border-[#002FA7] text-white' : 'border-[#E4E4E7] text-[#A1A1AA]'
                }`}>
                  2
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#09090B]">Análisis con IA</p>
                  <p className="text-xs text-[#71717A] mt-1">Identificación de riesgos</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 border-2 border-[#E4E4E7] flex items-center justify-center text-xs font-bold text-[#A1A1AA]">
                  3
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#09090B]">Matriz Generada</p>
                  <p className="text-xs text-[#71717A] mt-1">Descarga en Excel</p>
                </div>
              </div>
            </div>

            <button
              data-testid="analyze-button"
              onClick={handleUploadAndAnalyze}
              disabled={!file || uploading || analyzing}
              className="w-full bg-[#0A0A0A] text-white hover:bg-[#002FA7] font-semibold uppercase tracking-widest text-sm py-4 px-8 transition-colors border border-transparent hover:border-[#002FA7] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#0A0A0A]"
            >
              {uploading || analyzing ? 'PROCESANDO...' : 'GENERAR MATRIZ DE RIESGOS'}
            </button>
          </div>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border-2 border-[#E4E4E7] p-8 transition-all hover:border-[#0A0A0A] hover:shadow-brutal">
            <div className="text-[#002FA7] text-2xl font-bold mb-4" style={{ fontFamily: 'JetBrains Mono, monospace' }}>01</div>
            <h4 className="text-lg sm:text-xl font-semibold mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>PROCESAMIENTO AUTOMÁTICO</h4>
            <p className="text-sm text-[#52525B] leading-relaxed">Análisis inteligente de documentos PDF, Word y Excel mediante IA avanzada.</p>
          </div>
          
          <div className="bg-white border-2 border-[#E4E4E7] p-8 transition-all hover:border-[#0A0A0A] hover:shadow-brutal">
            <div className="text-[#002FA7] text-2xl font-bold mb-4" style={{ fontFamily: 'JetBrains Mono, monospace' }}>02</div>
            <h4 className="text-lg sm:text-xl font-semibold mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>IDENTIFICACIÓN DE RIESGOS</h4>
            <p className="text-sm text-[#52525B] leading-relaxed">Detección exhaustiva de riesgos legales en categorías: contractual, cumplimiento, laboral y más.</p>
          </div>
          
          <div className="bg-white border-2 border-[#E4E4E7] p-8 transition-all hover:border-[#0A0A0A] hover:shadow-brutal">
            <div className="text-[#002FA7] text-2xl font-bold mb-4" style={{ fontFamily: 'JetBrains Mono, monospace' }}>03</div>
            <h4 className="text-lg sm:text-xl font-semibold mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>MATRIZ EDITABLE</h4>
            <p className="text-sm text-[#52525B] leading-relaxed">Descarga tu matriz en formato Excel con clasificación de riesgos y recomendaciones.</p>
          </div>
        </div>
      </div>
    </div>
  );
}