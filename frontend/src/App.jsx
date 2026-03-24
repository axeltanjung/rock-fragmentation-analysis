import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AnalyzeImage from './pages/AnalyzeImage';
import Insights from './pages/Insights';
import Simulation from './pages/Simulation';

export default function App() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Router>
      <div className="flex h-screen bg-industrial-900">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
        <main className={`flex-1 overflow-auto transition-all duration-300 ${collapsed ? 'ml-16' : 'ml-60'}`}>
          <div className="p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analyze" element={<AnalyzeImage />} />
              <Route path="/insights" element={<Insights />} />
              <Route path="/simulation" element={<Simulation />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}
