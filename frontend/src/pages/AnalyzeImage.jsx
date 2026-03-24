import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, ZoomIn, ZoomOut } from 'lucide-react';
import { analyzeImage } from '../api';
import { PSDCurve, SizeHistogram } from '../components/Charts';
import { KPICard, InsightCard, RecommendationCard, QualityBadge, LoadingSpinner } from '../components/UIComponents';

export default function AnalyzeImage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scaleFactor, setScaleFactor] = useState(1.0);
  const [threshold, setThreshold] = useState(0.5);
  const [targetP80, setTargetP80] = useState(150);
  const [showOverlay, setShowOverlay] = useState(true);
  const [zoom, setZoom] = useState(1);

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      const f = accepted[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResults(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'] },
    maxFiles: 1,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeImage(file, scaleFactor, threshold, targetP80);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Analyze Image</h2>
        <p className="text-industrial-400 text-sm">Upload a post-blast image for fragmentation analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {!preview ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-blast-blue bg-blast-blue/10' : 'border-industrial-600 hover:border-industrial-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto text-industrial-400 mb-3" size={40} />
              <p className="text-industrial-300 text-sm">Drop image here or click to browse</p>
              <p className="text-industrial-500 text-xs mt-1">PNG, JPG, BMP, TIFF</p>
            </div>
          ) : (
            <div className="bg-industrial-800 rounded-xl border border-industrial-700 overflow-hidden">
              <div className="flex items-center justify-between p-3 border-b border-industrial-700">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowOverlay(!showOverlay)}
                    className={`text-xs px-3 py-1 rounded ${showOverlay ? 'bg-blast-blue/20 text-blast-blue' : 'bg-industrial-700 text-industrial-400'}`}
                  >
                    {showOverlay ? 'Overlay ON' : 'Overlay OFF'}
                  </button>
                  <button onClick={() => setZoom(z => Math.min(z + 0.25, 3))} className="text-industrial-400 hover:text-white p-1"><ZoomIn size={16} /></button>
                  <button onClick={() => setZoom(z => Math.max(z - 0.25, 0.5))} className="text-industrial-400 hover:text-white p-1"><ZoomOut size={16} /></button>
                  <span className="text-industrial-500 text-xs">{Math.round(zoom * 100)}%</span>
                </div>
                <button
                  onClick={() => { setFile(null); setPreview(null); setResults(null); }}
                  className="text-industrial-400 hover:text-white text-xs"
                >
                  Clear
                </button>
              </div>
              <div className="overflow-auto max-h-[500px] flex items-center justify-center bg-black/30 p-2">
                <img
                  src={results && showOverlay ? `data:image/png;base64,${results.overlay_image}` : preview}
                  alt="Analysis"
                  style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
                  className="max-w-full transition-transform"
                />
              </div>
            </div>
          )}

          {loading && <LoadingSpinner />}
          {error && <div className="bg-blast-red/10 border border-blast-red/30 rounded-lg p-3 text-blast-red text-sm">{error}</div>}

          {results && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KPICard title="P80" value={results.psd.p80} unit="mm" color={results.classification.quality_color} />
                <KPICard title="P50" value={results.psd.p50} unit="mm" color="blue" />
                <KPICard title="Fragments" value={results.num_fragments} color="orange" />
                <KPICard title="Score" value={results.classification.quality_score} unit="/100" color={results.classification.quality_color} />
              </div>

              <div className="flex items-center gap-3">
                <QualityBadge
                  quality={results.classification.quality}
                  label={results.classification.quality_label}
                  score={results.classification.quality_score}
                />
              </div>

              <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
                <h3 className="text-white font-semibold text-sm mb-3">Particle Size Distribution</h3>
                <PSDCurve
                  sizes={results.psd.sizes}
                  cumulativePassing={results.psd.cumulative_passing}
                  p80={results.psd.p80}
                  p50={results.psd.p50}
                />
              </div>

              <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700">
                <h3 className="text-white font-semibold text-sm mb-3">Size Histogram</h3>
                <SizeHistogram binEdges={results.psd.histogram.bin_edges} counts={results.psd.histogram.counts} />
              </div>

              <div className="space-y-3">
                <h3 className="text-white font-semibold text-sm">Insights</h3>
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
        </div>

        <div className="space-y-4">
          <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700 space-y-4">
            <h3 className="text-white font-semibold text-sm">Analysis Parameters</h3>
            <div>
              <label className="text-industrial-400 text-xs block mb-1">Scale Factor (mm/pixel)</label>
              <input
                type="number" step="0.1" min="0.1" value={scaleFactor}
                onChange={(e) => setScaleFactor(parseFloat(e.target.value) || 1)}
                className="w-full bg-industrial-700 rounded px-3 py-2 text-white text-sm border border-industrial-600 focus:border-blast-blue focus:outline-none"
              />
              <p className="text-industrial-500 text-[10px] mt-1">Set using a reference object in the image</p>
            </div>
            <div>
              <label className="text-industrial-400 text-xs block mb-1">Segmentation Threshold</label>
              <input
                type="range" min="0.1" max="0.9" step="0.05" value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full accent-blast-blue"
              />
              <span className="text-industrial-300 text-xs">{threshold.toFixed(2)}</span>
            </div>
            <div>
              <label className="text-industrial-400 text-xs block mb-1">Target P80 (mm)</label>
              <input
                type="number" step="10" min="10" value={targetP80}
                onChange={(e) => setTargetP80(parseFloat(e.target.value) || 150)}
                className="w-full bg-industrial-700 rounded px-3 py-2 text-white text-sm border border-industrial-600 focus:border-blast-blue focus:outline-none"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="w-full bg-blast-blue hover:bg-blast-blue/80 disabled:opacity-40 text-white py-2.5 rounded-lg text-sm font-semibold transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze Image'}
            </button>
          </div>

          {results && (
            <div className="bg-industrial-800 rounded-xl p-5 border border-industrial-700 space-y-2">
              <h3 className="text-white font-semibold text-sm">PSD Metrics</h3>
              <div className="text-sm space-y-1">
                {['p10', 'p20', 'p50', 'p80', 'p90', 'p100'].map(k => (
                  <div key={k} className="flex justify-between">
                    <span className="text-industrial-400 uppercase">{k}</span>
                    <span className="text-white">{results.psd[k]} mm</span>
                  </div>
                ))}
                <div className="border-t border-industrial-700 pt-1 mt-1">
                  <div className="flex justify-between">
                    <span className="text-industrial-400">Mean</span>
                    <span className="text-white">{results.psd.mean_size} mm</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-400">Cu</span>
                    <span className="text-white">{results.psd.uniformity_coefficient}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-industrial-400">Fines %</span>
                    <span className="text-white">{results.psd.fines_percentage}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
