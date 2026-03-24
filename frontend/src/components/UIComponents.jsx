export function KPICard({ title, value, unit, color = 'blue', subtitle }) {
  const colorMap = {
    green: 'border-blast-green text-blast-green',
    red: 'border-blast-red text-blast-red',
    yellow: 'border-blast-yellow text-blast-yellow',
    blue: 'border-blast-blue text-blast-blue',
    orange: 'border-blast-orange text-blast-orange',
  };
  const borderClass = colorMap[color] || colorMap.blue;

  return (
    <div className={`bg-industrial-800 rounded-xl p-4 border-l-4 ${borderClass.split(' ')[0]}`}>
      <p className="text-industrial-400 text-xs uppercase tracking-wide">{title}</p>
      <div className="flex items-baseline gap-1 mt-1">
        <span className={`text-2xl font-bold ${borderClass.split(' ')[1]}`}>{value}</span>
        {unit && <span className="text-industrial-400 text-sm">{unit}</span>}
      </div>
      {subtitle && <p className="text-industrial-500 text-xs mt-1">{subtitle}</p>}
    </div>
  );
}

export function InsightCard({ type, title, message }) {
  const styles = {
    success: { bg: 'bg-blast-green/10', border: 'border-blast-green/30', icon: '✓', color: 'text-blast-green' },
    warning: { bg: 'bg-blast-red/10', border: 'border-blast-red/30', icon: '!', color: 'text-blast-red' },
    caution: { bg: 'bg-blast-yellow/10', border: 'border-blast-yellow/30', icon: '⚠', color: 'text-blast-yellow' },
    info: { bg: 'bg-blast-blue/10', border: 'border-blast-blue/30', icon: 'ℹ', color: 'text-blast-blue' },
  };
  const s = styles[type] || styles.info;

  return (
    <div className={`${s.bg} border ${s.border} rounded-lg p-4`}>
      <div className="flex items-start gap-3">
        <span className={`${s.color} text-lg font-bold`}>{s.icon}</span>
        <div>
          <h4 className={`${s.color} font-semibold text-sm`}>{title}</h4>
          <p className="text-industrial-300 text-sm mt-1">{message}</p>
        </div>
      </div>
    </div>
  );
}

export function RecommendationCard({ priority, category, action, detail }) {
  const priorityColors = {
    high: 'bg-blast-red/20 text-blast-red border-blast-red/30',
    medium: 'bg-blast-yellow/20 text-blast-yellow border-blast-yellow/30',
    low: 'bg-blast-green/20 text-blast-green border-blast-green/30',
  };
  const cls = priorityColors[priority] || priorityColors.medium;

  return (
    <div className="bg-industrial-800 rounded-lg p-4 border border-industrial-700">
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${cls}`}>
          {priority}
        </span>
        <span className="text-industrial-400 text-xs">{category}</span>
      </div>
      <h4 className="text-white font-semibold text-sm">{action}</h4>
      <p className="text-industrial-400 text-sm mt-1">{detail}</p>
    </div>
  );
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blast-blue" />
    </div>
  );
}

export function QualityBadge({ quality, label, score }) {
  const colorMap = {
    fine: 'bg-blast-blue/20 text-blast-blue border-blast-blue/40',
    optimal: 'bg-blast-green/20 text-blast-green border-blast-green/40',
    slightly_coarse: 'bg-blast-yellow/20 text-blast-yellow border-blast-yellow/40',
    coarse: 'bg-blast-red/20 text-blast-red border-blast-red/40',
  };
  const cls = colorMap[quality] || colorMap.optimal;

  return (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${cls}`}>
      <span className="font-semibold text-sm">{label}</span>
      {score !== undefined && <span className="text-xs opacity-75">Score: {score}/100</span>}
    </div>
  );
}
