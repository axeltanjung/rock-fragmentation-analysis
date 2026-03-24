import { useState, useEffect, useCallback } from 'react';
import { computePSD } from '../api';
import { PSDCurve, SizeHistogram } from '../components/Charts';
import { KPICard, QualityBadge, InsightCard, LoadingSpinner } from '../components/UIComponents';

function generateSizes(mean, sigma, count) {
  const sizes = [];
  for (let i = 0; i < count; i++) {
    let u1 = 0, u2 = 0;
    while (u1 === 0) u1 = Math.random();
    while (u2 === 0) u2 = Math.random();
    const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    sizes.push(Math.exp(mean + sigma * z));
  }
  return sizes.filter(s => s > 0.5);
}

export default function Simulation() {
  const [meanLog, setMeanLog] = useState(3.0);
  const [sigmaLog, setSigmaLog] = useState(0.8);
  const [fragmentCount, setFragmentCount] = useState(50);
  const [scaleFactor, setScaleFactor] = useState(1.0);
  const [targetP80, setTargetP80] = useState(150);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const sizes = generateSizes(meanLog, sigmaLog, fragmentCount).map(s => s * scaleFactor);
      const data = await computePSD(sizes, scaleFactor, targetP80);
      setResults(data);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [meanLog, sigmaLog, fragmentCount, scaleFactor, targetP80]);

  useEffect(() => {
    const timer = setTimeout(runSimulation, 500);
    return () => clearTimeout(timer);
  }, [runSimulation]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Simulation</h2>
        <p className="text-industrial-400 text-sm">Adjust parameters to simulate different fragmentation outcomes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700 space-y-4">
          <h3 className="text-white font-semibold text-sm">Parameters</h3>

          <div>
            <label className="text-industrial-400 text-xs block mb-1">Size Distribution Mean (log)</label>
            <input type="range" min="1" max="5" step="0.1" value={meanLog} onChange={e => setMeanLog(parseFloat(e.target.value))} className="w-full accent-blast-blue" />
            <span className="text-industrial-300 text-xs">{meanLog.toFixed(1)} (avg ~{Math.exp(meanLog).toFixed(0)} mm)</span>
          </div>

          <div>
            <label className="text-industrial-400 text-xs block mb-1">Size Variability (sigma)</label>
            <input type="range" min="0.1" max="2.0" step="0.05" value={sigmaLog} onChange={e => setSigmaLog(parseFloat(e.target.value))} className="w-full accent-blast-blue" />
            <span className="text-industrial-300 text-xs">{sigmaLog.toFixed(2)}</span>
          </div>

          <div>
            <label className="text-industrial-400 text-xs block mb-1">Fragment Count</label>
            <input type="range" min="10" max="200" step="5" value={fragmentCount} onChange={e => setFragmentCount(parseInt(e.target.value))} className="w-full accent-blast-blue" />
            <span className="text-industrial-300 text-xs">{fragmentCount}</span>
          </div>

          <div>
            <label className="text-industrial-400 text-xs block mb-1">Scale Factor (mm/px)</label>
            <input
              type="number" step="0.1" min="0.1" value={scaleFactor}
              onChange={e => setScaleFactor(parseFloat(e.target.value) || 1)}
              className="w-full bg-industrial-700 rounded px-3 py-2 text-white text-sm border border-industrial-600 focus:border-blast-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="text-industrial-400 text-xs block mb-1">Target P80 (mm)</label>
            <input
              type="number" step="10" min="10" value={targetP80}
              onChange={e => setTargetP80(parseFloat(e.target.value) || 150)}
              className="w-full bg-industrial-700 rounded px-3 py-2 text-white text-sm border border-industrial-600 focus:border-blast-blue focus:outline-none"
            />
          </div>

          <div className="bg-industrial-700/50 rounded p-3 text-xs text-industrial-400">
            Lognormal distribution models real-world rock fragmentation. Adjust mean for average fragment size, sigma for spread.
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {loading && <LoadingSpinner />}

          {results && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KPICard title="P80" value={results.psd.p80} unit="mm" color={results.classification.quality_color} />
                <KPICard title="P50" value={results.psd.p50} unit="mm" color="blue" />
                <KPICard title="Fines" value={results.psd.fines_percentage} unit="%" color={results.psd.fines_percentage > 20 ? 'red' : 'green'} />
                <KPICard title="Cu" value={results.psd.uniformity_coefficient} color="orange" />
              </div>

              <QualityBadge
                quality={results.classification.quality}
                label={results.classification.quality_label}
                score={results.classification.quality_score}
              />

              <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
                <h3 className="text-white font-semibold text-sm mb-3">Simulated PSD</h3>
                <PSDCurve
                  sizes={results.psd.sizes}
                  cumulativePassing={results.psd.cumulative_passing}
                  p80={results.psd.p80}
                  p50={results.psd.p50}
                />
              </div>

              <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
                <h3 className="text-white font-semibold text-sm mb-3">Histogram</h3>
                <SizeHistogram binEdges={results.psd.histogram.bin_edges} counts={results.psd.histogram.counts} />
              </div>

              <div className="space-y-3">
                <h3 className="text-white font-semibold text-sm">Insights</h3>
                {results.insights.map((ins, i) => (
                  <InsightCard key={i} type={ins.type} title={ins.title} message={ins.message} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
