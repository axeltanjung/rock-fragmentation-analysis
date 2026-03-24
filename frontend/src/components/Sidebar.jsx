import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ImagePlus, Lightbulb, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analyze', label: 'Analyze Image', icon: ImagePlus },
  { path: '/insights', label: 'Insights', icon: Lightbulb },
  { path: '/simulation', label: 'Simulation', icon: SlidersHorizontal },
];

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <div className={`fixed left-0 top-0 h-full bg-industrial-800 border-r border-industrial-700 transition-all duration-300 z-50 flex flex-col ${collapsed ? 'w-16' : 'w-60'}`}>
      <div className="flex items-center justify-between p-4 border-b border-industrial-700">
        {!collapsed && (
          <div>
            <h1 className="text-sm font-bold text-white">FragAnalyzer</h1>
            <p className="text-[10px] text-industrial-400">Rock Fragmentation</p>
          </div>
        )}
        <button onClick={onToggle} className="text-industrial-400 hover:text-white p-1 rounded hover:bg-industrial-700">
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blast-blue/20 text-blast-blue border border-blast-blue/30'
                  : 'text-industrial-400 hover:text-white hover:bg-industrial-700'
              }`
            }
          >
            <Icon size={18} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="p-4 border-t border-industrial-700">
          <p className="text-[10px] text-industrial-500 text-center">v1.0.0 | Mining CV</p>
        </div>
      )}
    </div>
  );
}
