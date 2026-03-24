import io
import base64
import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.inference import DemoInference, FragmentationInference
from ..analysis.fragmentation import compute_psd, compute_psd_from_sizes
from ..analysis.insights import classify_fragmentation, generate_insights, generate_recommendations

router = APIRouter()

inference_engine = DemoInference()


class AnalysisRequest(BaseModel):
    scale_factor: float = 1.0
    threshold: float = 0.5
    target_p80: float = 150.0


class SimulationRequest(BaseModel):
    sizes: list[float]
    scale_factor: float = 1.0
    target_p80: float = 150.0


class InsightsRequest(BaseModel):
    p80: float
    p50: float
    p10: float = 0.0
    p20: float = 0.0
    p90: float = 0.0
    fines_percentage: float = 0.0
    uniformity_coefficient: float = 0.0
    target_p80: float = 150.0


def mask_to_overlay(image: Image.Image, labeled_mask: np.ndarray) -> str:
    img_array = np.array(image.convert("RGBA"))
    overlay = img_array.copy()

    unique_labels = np.unique(labeled_mask)
    unique_labels = unique_labels[unique_labels > 0]

    np.random.seed(42)
    colors = np.random.randint(50, 255, size=(len(unique_labels) + 1, 3))

    for i, label in enumerate(unique_labels):
        mask = labeled_mask == label
        color = colors[i]
        overlay[mask, 0] = np.clip(
            img_array[mask, 0].astype(int) * 0.5 + color[0] * 0.5, 0, 255
        ).astype(np.uint8)
        overlay[mask, 1] = np.clip(
            img_array[mask, 1].astype(int) * 0.5 + color[1] * 0.5, 0, 255
        ).astype(np.uint8)
        overlay[mask, 2] = np.clip(
            img_array[mask, 2].astype(int) * 0.5 + color[2] * 0.5, 0, 255
        ).astype(np.uint8)
        overlay[mask, 3] = 200

    from scipy.ndimage import binary_erosion
    for label in unique_labels:
        mask = labeled_mask == label
        eroded = binary_erosion(mask, iterations=1)
        boundary = mask & ~eroded
        overlay[boundary, 0] = 255
        overlay[boundary, 1] = 255
        overlay[boundary, 2] = 0
        overlay[boundary, 3] = 255

    pil_overlay = Image.fromarray(overlay)
    buffer = io.BytesIO()
    pil_overlay.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@router.post("/analyze_image")
async def analyze_image(
    file: UploadFile = File(...),
    scale_factor: float = Form(1.0),
    threshold: float = Form(0.5),
    target_p80: float = Form(150.0),
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    results = inference_engine.analyze(image, scale_factor=scale_factor, threshold=threshold)

    overlay_b64 = mask_to_overlay(image, results["labeled_mask"])

    psd = results["psd"]
    classification = classify_fragmentation(psd, target_p80=target_p80)
    insights = generate_insights(psd, classification)
    recommendations = generate_recommendations(psd, classification)

    return {
        "overlay_image": overlay_b64,
        "num_fragments": results["num_fragments"],
        "fragments": results["fragments"][:100],
        "psd": psd,
        "classification": classification,
        "insights": insights,
        "recommendations": recommendations,
        "image_size": {"width": image.width, "height": image.height},
        "scale_factor": scale_factor,
    }


@router.post("/compute_psd")
async def compute_psd_endpoint(request: SimulationRequest):
    psd = compute_psd_from_sizes(request.sizes)
    classification = classify_fragmentation(psd, target_p80=request.target_p80)
    insights = generate_insights(psd, classification)
    recommendations = generate_recommendations(psd, classification)

    return {
        "psd": psd,
        "classification": classification,
        "insights": insights,
        "recommendations": recommendations,
    }


@router.post("/insights")
async def get_insights(request: InsightsRequest):
    psd = {
        "p80": request.p80,
        "p50": request.p50,
        "p10": request.p10,
        "p20": request.p20,
        "p90": request.p90,
        "fines_percentage": request.fines_percentage,
        "uniformity_coefficient": request.uniformity_coefficient,
    }
    classification = classify_fragmentation(psd, target_p80=request.target_p80)
    insights = generate_insights(psd, classification)
    recommendations = generate_recommendations(psd, classification)

    return {
        "classification": classification,
        "insights": insights,
        "recommendations": recommendations,
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": inference_engine.model is not None or isinstance(inference_engine, DemoInference)}
