import { useState } from 'react';
import { getInsights } from '../api';
import { InsightCard, RecommendationCard, QualityBadge, LoadingSpinner } from '../components/UIComponents';

export default function Insights() {
  const [form, setForm] = useState({ p80: 160, p50: 95, p10: 15, p20: 35, p90: 210, fines_percentage: 12, uniformity_coefficient: 4.5, target_p80: 150 });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await getInsights(form);
      setResults(data);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) => setForm(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Fragmentation Insights</h2>
        <p className="text-industrial-400 text-sm">Enter PSD metrics to get actionable insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
          <h3 className="text-white font-semibold text-sm mb-4">Input Metrics</h3>
          <form onSubmit={handleSubmit} className="space-y-3">
            {[
              ['p80', 'P80 (mm)'], ['p50', 'P50 (mm)'], ['p10', 'P10 (mm)'],
              ['p20', 'P20 (mm)'], ['p90', 'P90 (mm)'], ['fines_percentage', 'Fines (%)'],
              ['uniformity_coefficient', 'Cu'], ['target_p80', 'Target P80 (mm)'],
            ].map(([key, label]) => (
              <div key={key}>
                <label className="text-industrial-400 text-xs">{label}</label>
                <input
                  type="number" step="0.1" value={form[key]}
                  onChange={(e) => updateField(key, e.target.value)}
                  className="w-full bg-industrial-700 rounded px-3 py-2 text-white text-sm border border-industrial-600 focus:border-blast-blue focus:outline-none"
                />
              </div>
            ))}
            <button
              type="submit" disabled={loading}
              className="w-full bg-blast-blue hover:bg-blast-blue/80 disabled:opacity-40 text-white py-2.5 rounded-lg text-sm font-semibold"
            >
              {loading ? 'Processing...' : 'Generate Insights'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {loading && <LoadingSpinner />}

          {results && (
            <>
              <div className="flex items-center gap-3">
                <QualityBadge
                  quality={results.classification.quality}
                  label={results.classification.quality_label}
                  score={results.classification.quality_score}
                />
                <span className="text-industrial-400 text-sm">
                  P80 deviation: <span className={results.classification.p80_deviation > 0 ? 'text-blast-red' : 'text-blast-green'}>
                    {results.classification.p80_deviation > 0 ? '+' : ''}{results.classification.p80_deviation}%
                  </span>
                </span>
              </div>

              <div className="space-y-3">
                <h3 className="text-white font-semibold text-sm">Analysis Insights</h3>
                {results.insights.map((ins, i) => (
                  <InsightCard key={i} type={ins.type} title={ins.title} message={ins.message} />
                ))}
              </div>

              <div className="space-y-3">
                <h3 className="text-white font-semibold text-sm">Recommendations</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {results.recommendations.map((rec, i) => (
                    <RecommendationCard key={i} {...rec} />
                  ))}
                </div>
              </div>
            </>
          )}

          {!results && !loading && (
            <div className="bg-industrial-800 rounded-xl p-12 border border-industrial-700 text-center">
              <p className="text-industrial-400">Enter PSD metrics on the left and click Generate Insights</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
