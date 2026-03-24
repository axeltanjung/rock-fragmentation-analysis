import Plot from 'react-plotly.js';

export function PSDCurve({ sizes = [], cumulativePassing = [], p80, p50 }) {
  if (!sizes.length) return null;

  const traces = [
    {
      x: sizes,
      y: cumulativePassing,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'PSD Curve',
      line: { color: '#3b82f6', width: 2 },
      marker: { size: 3 },
    },
  ];

  const shapes = [];
  const annotations = [];

  if (p80 > 0) {
    shapes.push({
      type: 'line', x0: p80, x1: p80, y0: 0, y1: 80,
      line: { color: '#ef4444', width: 2, dash: 'dash' },
    });
    shapes.push({
      type: 'line', x0: 0, x1: p80, y0: 80, y1: 80,
      line: { color: '#ef4444', width: 1, dash: 'dot' },
    });
    annotations.push({
      x: Math.log10(p80), y: 85, text: `P80 = ${p80.toFixed(1)} mm`,
      showarrow: false, font: { color: '#ef4444', size: 11 },
    });
  }

  if (p50 > 0) {
    shapes.push({
      type: 'line', x0: p50, x1: p50, y0: 0, y1: 50,
      line: { color: '#22c55e', width: 2, dash: 'dash' },
    });
    annotations.push({
      x: Math.log10(p50), y: 55, text: `P50 = ${p50.toFixed(1)} mm`,
      showarrow: false, font: { color: '#22c55e', size: 11 },
    });
  }

  return (
    <Plot
      data={traces}
      layout={{
        xaxis: { title: 'Fragment Size (mm)', type: 'log', gridcolor: '#334155', color: '#94a3b8' },
        yaxis: { title: 'Cumulative Passing (%)', range: [0, 105], gridcolor: '#334155', color: '#94a3b8' },
        shapes,
        annotations,
        plot_bgcolor: '#1e293b',
        paper_bgcolor: '#1e293b',
        font: { color: '#94a3b8' },
        margin: { t: 30, r: 20, b: 50, l: 60 },
        showlegend: false,
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '350px' }}
    />
  );
}

export function SizeHistogram({ binEdges = [], counts = [] }) {
  if (!binEdges.length || !counts.length) return null;

  const midpoints = binEdges.slice(0, -1).map((e, i) => (e + binEdges[i + 1]) / 2);

  return (
    <Plot
      data={[
        {
          x: midpoints,
          y: counts,
          type: 'bar',
          marker: {
            color: counts.map((_, i) => {
              const ratio = i / counts.length;
              if (ratio < 0.3) return '#3b82f6';
              if (ratio < 0.7) return '#22c55e';
              return '#ef4444';
            }),
          },
        },
      ]}
      layout={{
        xaxis: { title: 'Fragment Size (mm)', type: 'log', gridcolor: '#334155', color: '#94a3b8' },
        yaxis: { title: 'Count', gridcolor: '#334155', color: '#94a3b8' },
        plot_bgcolor: '#1e293b',
        paper_bgcolor: '#1e293b',
        font: { color: '#94a3b8' },
        margin: { t: 20, r: 20, b: 50, l: 60 },
        bargap: 0.05,
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '300px' }}
    />
  );
}
