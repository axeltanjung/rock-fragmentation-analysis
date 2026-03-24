import numpy as np
from typing import List, Dict, Any


def compute_fragment_properties(
    labeled_mask: np.ndarray, scale_factor: float = 1.0
) -> List[Dict[str, Any]]:
    fragments = []
    unique_labels = np.unique(labeled_mask)
    unique_labels = unique_labels[unique_labels > 0]

    for label_id in unique_labels:
        region = (labeled_mask == label_id)
        area_pixels = int(np.sum(region))

        if area_pixels < 10:
            continue

        area_mm2 = area_pixels * (scale_factor ** 2)
        equivalent_diameter_mm = 2.0 * np.sqrt(area_mm2 / np.pi)

        ys, xs = np.where(region)
        centroid_x = float(np.mean(xs))
        centroid_y = float(np.mean(ys))

        bbox_x_min = int(np.min(xs))
        bbox_x_max = int(np.max(xs))
        bbox_y_min = int(np.min(ys))
        bbox_y_max = int(np.max(ys))
        bbox_width = (bbox_x_max - bbox_x_min) * scale_factor
        bbox_height = (bbox_y_max - bbox_y_min) * scale_factor

        major_axis = max(bbox_width, bbox_height)
        minor_axis = min(bbox_width, bbox_height)
        aspect_ratio = major_axis / minor_axis if minor_axis > 0 else 1.0

        perimeter_pixels = _compute_perimeter(region)
        perimeter_mm = perimeter_pixels * scale_factor

        if perimeter_mm > 0:
            circularity = (4.0 * np.pi * area_mm2) / (perimeter_mm ** 2)
        else:
            circularity = 0.0

        fragments.append({
            "id": int(label_id),
            "area_pixels": area_pixels,
            "area_mm2": round(area_mm2, 2),
            "equivalent_diameter_mm": round(equivalent_diameter_mm, 2),
            "centroid": [round(centroid_x, 1), round(centroid_y, 1)],
            "bbox": [bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max],
            "major_axis_mm": round(major_axis, 2),
            "minor_axis_mm": round(minor_axis, 2),
            "aspect_ratio": round(aspect_ratio, 3),
            "perimeter_mm": round(perimeter_mm, 2),
            "circularity": round(min(circularity, 1.0), 3),
        })

    fragments.sort(key=lambda f: f["equivalent_diameter_mm"])
    return fragments


def _compute_perimeter(binary_region: np.ndarray) -> float:
    from scipy.ndimage import binary_erosion
    eroded = binary_erosion(binary_region)
    boundary = binary_region.astype(int) - eroded.astype(int)
    return float(np.sum(boundary))


def compute_psd(fragments: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not fragments:
        return {
            "sizes": [],
            "cumulative_passing": [],
            "p10": 0.0,
            "p20": 0.0,
            "p50": 0.0,
            "p80": 0.0,
            "p90": 0.0,
            "p100": 0.0,
            "mean_size": 0.0,
            "std_size": 0.0,
            "uniformity_coefficient": 0.0,
            "top_size": 0.0,
            "fines_percentage": 0.0,
            "histogram": {"bin_edges": [], "counts": []},
        }

    diameters = np.array([f["equivalent_diameter_mm"] for f in fragments])
    areas = np.array([f["area_mm2"] for f in fragments])

    sorted_indices = np.argsort(diameters)
    sorted_diameters = diameters[sorted_indices]
    sorted_areas = areas[sorted_indices]

    total_area = np.sum(sorted_areas)
    if total_area > 0:
        cumulative_area = np.cumsum(sorted_areas)
        cumulative_passing = (cumulative_area / total_area * 100.0).tolist()
    else:
        cumulative_passing = np.linspace(0, 100, len(sorted_diameters)).tolist()

    sizes = sorted_diameters.tolist()

    def interpolate_percentile(target_pct):
        cp = np.array(cumulative_passing)
        if len(cp) == 0:
            return 0.0
        if target_pct <= cp[0]:
            return sizes[0]
        if target_pct >= cp[-1]:
            return sizes[-1]
        idx = np.searchsorted(cp, target_pct)
        if idx == 0:
            return sizes[0]
        x0, x1 = sizes[idx - 1], sizes[idx]
        y0, y1 = cp[idx - 1], cp[idx]
        if y1 == y0:
            return x0
        return x0 + (target_pct - y0) * (x1 - x0) / (y1 - y0)

    p10 = interpolate_percentile(10)
    p20 = interpolate_percentile(20)
    p50 = interpolate_percentile(50)
    p80 = interpolate_percentile(80)
    p90 = interpolate_percentile(90)
    p100 = float(sorted_diameters[-1]) if len(sorted_diameters) > 0 else 0.0

    mean_size = float(np.mean(diameters))
    std_size = float(np.std(diameters))

    cu = p80 / p20 if p20 > 0 else 0.0

    fines_threshold = p50 * 0.25
    fines_count = int(np.sum(diameters < fines_threshold))
    fines_percentage = (fines_count / len(diameters) * 100.0) if len(diameters) > 0 else 0.0

    n_bins = min(30, max(5, len(diameters) // 5))
    if len(diameters) > 0:
        log_diameters = np.log10(np.maximum(diameters, 0.1))
        counts, bin_edges = np.histogram(log_diameters, bins=n_bins)
        bin_edges_linear = (10 ** bin_edges).tolist()
        hist_counts = counts.tolist()
    else:
        bin_edges_linear = []
        hist_counts = []

    return {
        "sizes": [round(s, 2) for s in sizes],
        "cumulative_passing": [round(c, 2) for c in cumulative_passing],
        "p10": round(p10, 2),
        "p20": round(p20, 2),
        "p50": round(p50, 2),
        "p80": round(p80, 2),
        "p90": round(p90, 2),
        "p100": round(p100, 2),
        "mean_size": round(mean_size, 2),
        "std_size": round(std_size, 2),
        "uniformity_coefficient": round(cu, 2),
        "top_size": round(p100, 2),
        "fines_percentage": round(fines_percentage, 2),
        "histogram": {"bin_edges": [round(b, 2) for b in bin_edges_linear], "counts": hist_counts},
    }


def compute_psd_from_sizes(
    diameters_mm: List[float],
) -> Dict[str, Any]:
    if not diameters_mm:
        return compute_psd([])

    fake_fragments = []
    for i, d in enumerate(diameters_mm):
        area = np.pi * (d / 2.0) ** 2
        fake_fragments.append({
            "id": i + 1,
            "area_mm2": area,
            "equivalent_diameter_mm": d,
        })
    return compute_psd(fake_fragments)
