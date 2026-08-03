import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Home from '../pages/Home'
import Dashboard from '../pages/Dashboard'
import AnalyticsPage from '../pages/AnalyticsPage'
import LoginPage from '../pages/LoginPage'
import RegisterPage from '../pages/RegisterPage'

export default function AppRouter() {
  const token = localStorage.getItem('shortify_access_token')

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/dashboard"
          element={token ? <Dashboard /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/analytics/:id"
          element={token ? <AnalyticsPage /> : <Navigate to="/login" replace />}
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  )
}
