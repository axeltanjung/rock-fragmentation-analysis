import { KPICard } from '../components/UIComponents';
import { PSDCurve } from '../components/Charts';

const demoData = {
  avgP80: 142.5,
  avgP50: 89.3,
  qualityScore: 78,
  blastsWithinTarget: 72,
  totalBlasts: 15,
  recentResults: [
    { id: 'B-001', p80: 135.2, p50: 82.1, quality: 'optimal' },
    { id: 'B-002', p80: 198.7, p50: 121.3, quality: 'coarse' },
    { id: 'B-003', p80: 112.4, p50: 68.9, quality: 'fine' },
    { id: 'B-004', p80: 155.1, p50: 95.2, quality: 'slightly_coarse' },
    { id: 'B-005', p80: 141.0, p50: 87.6, quality: 'optimal' },
  ],
  avgPSD: {
    sizes: [5, 10, 20, 40, 60, 80, 100, 120, 142.5, 180, 220, 280],
    cumulativePassing: [2, 8, 18, 35, 48, 62, 73, 82, 90, 95, 98, 100],
  },
};

const qualityColors = {
  fine: 'text-blast-blue',
  optimal: 'text-blast-green',
  slightly_coarse: 'text-blast-yellow',
  coarse: 'text-blast-red',
};

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-industrial-400 text-sm">Rock fragmentation overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Average P80" value={demoData.avgP80} unit="mm" color="blue" subtitle="Last 15 blasts" />
        <KPICard title="Quality Score" value={demoData.qualityScore} unit="/100" color="green" subtitle="Overall performance" />
        <KPICard
          title="Within Target"
          value={`${demoData.blastsWithinTarget}%`}
          color={demoData.blastsWithinTarget >= 70 ? 'green' : 'yellow'}
          subtitle={`${Math.round(demoData.totalBlasts * demoData.blastsWithinTarget / 100)}/${demoData.totalBlasts} blasts`}
        />
        <KPICard title="Average P50" value={demoData.avgP50} unit="mm" color="orange" subtitle="Median fragment size" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
          <h3 className="text-white font-semibold text-sm mb-3">Avg Particle Size Distribution</h3>
          <PSDCurve
            sizes={demoData.avgPSD.sizes}
            cumulativePassing={demoData.avgPSD.cumulativePassing}
            p80={demoData.avgP80}
            p50={demoData.avgP50}
          />
        </div>

        <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
          <h3 className="text-white font-semibold text-sm mb-3">Recent Blast Results</h3>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-industrial-400 border-b border-industrial-700">
                  <th className="text-left py-2 px-3">Blast ID</th>
                  <th className="text-right py-2 px-3">P80 (mm)</th>
                  <th className="text-right py-2 px-3">P50 (mm)</th>
                  <th className="text-left py-2 px-3">Quality</th>
                </tr>
              </thead>
              <tbody>
                {demoData.recentResults.map((r) => (
                  <tr key={r.id} className="border-b border-industrial-700/50 hover:bg-industrial-700/30">
                    <td className="py-2 px-3 text-white font-mono">{r.id}</td>
                    <td className="py-2 px-3 text-right text-industrial-300">{r.p80}</td>
                    <td className="py-2 px-3 text-right text-industrial-300">{r.p50}</td>
                    <td className={`py-2 px-3 capitalize ${qualityColors[r.quality]}`}>
                      {r.quality.replace('_', ' ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
