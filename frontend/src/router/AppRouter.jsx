import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Home from '../pages/Home'
import Dashboard from '../pages/Dashboard'
import AnalyticsPage from '../pages/AnalyticsPage'

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics/:id" element={<AnalyticsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
