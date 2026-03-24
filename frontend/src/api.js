const API_BASE = '/api/v1';

export async function analyzeImage(file, scaleFactor = 1.0, threshold = 0.5, targetP80 = 150.0) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('scale_factor', scaleFactor.toString());
  formData.append('threshold', threshold.toString());
  formData.append('target_p80', targetP80.toString());

  const response = await fetch(`${API_BASE}/analyze_image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(error.detail || 'Analysis failed');
  }

  return response.json();
}

export async function computePSD(sizes, scaleFactor = 1.0, targetP80 = 150.0) {
  const response = await fetch(`${API_BASE}/compute_psd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sizes, scale_factor: scaleFactor, target_p80: targetP80 }),
  });

  if (!response.ok) throw new Error('PSD computation failed');
  return response.json();
}

export async function getInsights(metrics) {
  const response = await fetch(`${API_BASE}/insights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metrics),
  });

  if (!response.ok) throw new Error('Insights generation failed');
  return response.json();
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
