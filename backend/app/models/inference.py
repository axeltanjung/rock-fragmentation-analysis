import io
import numpy as np
import torch
from PIL import Image
from scipy import ndimage
from ..models.unet import UNet
from ..analysis.fragmentation import compute_fragment_properties, compute_psd


class FragmentationInference:
    def __init__(self, model_path: str = None, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = UNet(n_channels=3, n_classes=1, bilinear=False)

        if model_path:
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)

        self.model.to(self.device)
        self.model.eval()
        self.input_size = (256, 256)

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        original_size = image.size
        image = image.resize(self.input_size, Image.BILINEAR)
        img_array = np.array(image).astype(np.float32) / 255.0
        if img_array.ndim == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]
        tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).unsqueeze(0)
        return tensor.to(self.device), original_size

    def segment(self, image: Image.Image, threshold: float = 0.5):
        tensor, original_size = self.preprocess(image)
        with torch.no_grad():
            output = self.model(tensor)
            prob_map = torch.sigmoid(output).squeeze().cpu().numpy()

        binary_mask = (prob_map > threshold).astype(np.uint8)
        labeled_mask, num_features = ndimage.label(binary_mask)

        mask_resized = np.array(
            Image.fromarray(labeled_mask.astype(np.float32)).resize(
                original_size, Image.NEAREST
            )
        ).astype(np.int32)

        return mask_resized, num_features, prob_map

    def analyze(
        self,
        image: Image.Image,
        scale_factor: float = 1.0,
        threshold: float = 0.5,
    ):
        labeled_mask, num_fragments, prob_map = self.segment(image, threshold)
        fragments = compute_fragment_properties(labeled_mask, scale_factor)
        psd_data = compute_psd(fragments)

        return {
            "labeled_mask": labeled_mask,
            "num_fragments": num_fragments,
            "prob_map": prob_map,
            "fragments": fragments,
            "psd": psd_data,
        }


class DemoInference(FragmentationInference):
    def __init__(self):
        self.device = torch.device("cpu")
        self.model = None
        self.input_size = (256, 256)

    def segment(self, image: Image.Image, threshold: float = 0.5):
        img_array = np.array(image.convert("L").resize(self.input_size))
        edges = self._detect_edges(img_array)
        binary = (edges > threshold * 255).astype(np.uint8)
        binary = ndimage.binary_fill_holes(binary).astype(np.uint8)
        labeled_mask, num_features = ndimage.label(1 - binary)

        min_area = 50
        for i in range(1, num_features + 1):
            if np.sum(labeled_mask == i) < min_area:
                labeled_mask[labeled_mask == i] = 0

        unique_labels = np.unique(labeled_mask)
        unique_labels = unique_labels[unique_labels > 0]
        new_mask = np.zeros_like(labeled_mask)
        for new_id, old_id in enumerate(unique_labels, 1):
            new_mask[labeled_mask == old_id] = new_id

        original_size = image.size
        mask_resized = np.array(
            Image.fromarray(new_mask.astype(np.float32)).resize(
                original_size, Image.NEAREST
            )
        ).astype(np.int32)

        return mask_resized, len(unique_labels), edges.astype(np.float32) / 255.0

    def _detect_edges(self, gray_image: np.ndarray) -> np.ndarray:
        from scipy.ndimage import gaussian_filter, sobel

        smoothed = gaussian_filter(gray_image.astype(np.float64), sigma=2.0)
        sx = sobel(smoothed, axis=0)
        sy = sobel(smoothed, axis=1)
        edges = np.hypot(sx, sy)
        edges = (edges / edges.max() * 255).astype(np.uint8)
        return edges
