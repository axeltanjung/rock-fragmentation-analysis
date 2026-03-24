# Rock Fragmentation Analysis System

A decision-support system for mining operations that analyzes post-blast images to estimate particle size distribution (PSD), compute key fragmentation metrics, and provide actionable insights for blast optimization and downstream processing.

---

## Features

### Computer Vision Pipeline
- **U-Net Segmentation Model** — Encoder-decoder architecture with skip connections for pixel-level rock fragment detection
- **Demo Mode** — Edge-detection based fallback that works without a trained model
- **Synthetic Dataset Generator** — Produces 1000+ images with lognormal fragment size distributions simulating fine, coarse, and mixed fragmentation

### Fragmentation Analysis
- Segment individual rock fragments from images
- Compute area, equivalent diameter, aspect ratio, circularity per fragment
- Generate **Particle Size Distribution (PSD)** curves on log scale
- Calculate **P10, P20, P50, P80, P90, P100**
- Uniformity coefficient (Cu) and fines percentage

### Insights & Blast Optimization
- Fragmentation quality classification: `fine` | `optimal` | `slightly_coarse` | `coarse`
- Quality scoring (0–100)
- Actionable recommendations:

| Problem | Recommendation |
|---|---|
| P80 too high | Increase powder factor, reduce burden/spacing |
| Excessive fines | Reduce explosive energy |
| Wide distribution | Check geology or blast timing |
| Crushing risk | Alert on energy consumption increase |

### Web Application
- **Dashboard** — Average P80, quality score, % blasts within target, recent results table
- **Analyze Image** — Upload image → segmented overlay, PSD curve, histogram, insights, recommendations
- **Insights** — Manual metric input for standalone analysis
- **Simulation** — Interactive sliders (mean, sigma, count, scale, target P80) with live PSD updates

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, PyTorch |
| CV Model | U-Net (custom implementation) |
| Frontend | React 18, Tailwind CSS, Plotly.js |
| Deployment | Docker, docker-compose, Nginx |

---

## Project Structure

```
rock-fragmentation-analysis/
├── backend/
│   ├── app/
│   │   ├── api/routes.py              # FastAPI endpoints
│   │   ├── analysis/
│   │   │   ├── fragmentation.py       # PSD computation, fragment properties
│   │   │   └── insights.py            # Classification, insights, recommendations
│   │   ├── dataset/
│   │   │   ├── generator.py           # Synthetic image generator (lognormal)
│   │   │   └── augmentation.py        # Data augmentation pipeline
│   │   ├── models/
│   │   │   ├── unet.py                # U-Net architecture
│   │   │   └── inference.py           # Segmentation inference engine
│   │   └── main.py                    # FastAPI app entry point
│   ├── train.py                       # Model training script
│   ├── generate_dataset.py            # Dataset generation CLI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx          # Overview with KPIs
│   │   │   ├── AnalyzeImage.jsx       # Image upload & analysis
│   │   │   ├── Insights.jsx           # Manual metrics input
│   │   │   └── Simulation.jsx         # Interactive PSD simulation
│   │   ├── components/
│   │   │   ├── Charts.jsx             # PSD curve & histogram (Plotly)
│   │   │   ├── Sidebar.jsx            # Navigation
│   │   │   └── UIComponents.jsx       # KPI cards, badges, alerts
│   │   ├── api.js                     # API client
│   │   └── App.jsx                    # Router setup
│   └── package.json
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── nginx.conf
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for containerized deployment)

### Option 1: Docker (Recommended)

```bash
cd rock-fragmentation-analysis
docker-compose up --build
```

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**
```bash
cd rock-fragmentation-analysis/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd rock-fragmentation-analysis/frontend
npm install
npm run dev
```

---

## Training the Model

### 1. Generate Synthetic Dataset

```bash
cd backend
python generate_dataset.py --n-images 1000 --image-size 256
```

This creates `data/synthetic/` with:
- `images/` — RGB rock fragment images
- `masks/` — Binary segmentation masks
- `metadata.json` — Fragment counts, sizes, quality labels

Fragment sizes follow a **lognormal distribution** (matching real-world fragmentation):
```python
sizes = np.random.lognormal(mean=3, sigma=1, size=n_fragments)
```

### 2. Train U-Net

```bash
python train.py --epochs 50 --batch-size 8 --lr 0.001
```

- Loss: BCE + Dice (combined)
- Optimizer: AdamW with gradient clipping
- Early stopping with patience=10
- Saves `models/best_model.pth`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze_image` | Upload image → segmentation + PSD + insights |
| `POST` | `/api/v1/compute_psd` | Compute PSD from size array |
| `POST` | `/api/v1/insights` | Generate insights from PSD metrics |
| `GET` | `/api/v1/health` | Health check |

### Example: Analyze Image

```bash
curl -X POST http://localhost:8000/api/v1/analyze_image \
  -F "file=@blast_photo.jpg" \
  -F "scale_factor=2.5" \
  -F "threshold=0.5" \
  -F "target_p80=150"
```

Response includes: overlay image (base64), fragment list, PSD metrics, classification, insights, and recommendations.

---

## Scale Calibration

The system converts pixel measurements to millimeters using a **scale factor** (mm/pixel). To calibrate:

1. Place a reference object of known size in the image
2. Measure its pixel width in the image
3. Compute: `scale_factor = known_size_mm / pixel_width`
4. Enter this value in the analysis parameters

---

## Key Design Decisions

- **Lognormal distribution** for synthetic data — matches real fragmentation physics (Kuz-Ram model)
- **Area-weighted PSD** — larger fragments contribute proportionally more to the distribution
- **Edge-detection fallback** (DemoInference) — allows the app to function without a trained model
- **Combined BCE + Dice loss** — handles class imbalance in segmentation
- **Equivalent diameter** = `2 * sqrt(area / π)` — standard in mineral processing

---

## Deployment

Supports deployment on:
- **Local** — Docker Compose
- **AWS** — ECS/Fargate or EC2
- **GCP** — Cloud Run or GKE
- **Render** — Direct Docker deployment
