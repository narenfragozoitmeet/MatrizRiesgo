import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalysisGTC45Page from './pages/AnalysisGTC45Page';
import DashboardPage from './pages/DashboardPage';
import HistoryGTC45Page from './pages/HistoryGTC45Page';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/gtc45/:matrizId" element={<AnalysisGTC45Page />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/history" element={<HistoryGTC45Page />} />
      </Routes>
    </BrowserRouter>
  );
}