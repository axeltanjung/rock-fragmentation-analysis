import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import json
from typing import Tuple, List


class SyntheticRockDataset
    def __init__(
        self,
        image_size Tuple[int, int] = (256, 256),
        output_dir str = datasynthetic,
    )
        self.image_size = image_size
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir  images
        self.masks_dir = self.output_dir  masks

    def generate_fragment(self, center, size, irregularity=0.4, spikiness=0.2)
        num_vertices = np.random.randint(6, 14)
        angles = np.sort(
            np.random.uniform(0, 2  np.pi, num_vertices)
        )
        radii = []
        for _ in range(num_vertices)
            r = size  (1 + np.random.normal(0, irregularity))
            r = max(r, size  0.3)
            radii.append(r)

        points = []
        for angle, radius in zip(angles, radii)
            spike = np.random.normal(0, spikiness  size)
            r = radius + spike
            r = max(r, 2)
            x = center[0] + r  np.cos(angle)
            y = center[1] + r  np.sin(angle)
            points.append((int(x), int(y)))
        return points

    def generate_rock_texture(self, mask_region np.ndarray) - np.ndarray
        h, w = mask_region.shape[2]
        base_color = np.random.randint(80, 180)
        texture = np.full((h, w, 3), base_color, dtype=np.uint8)

        noise = np.random.normal(0, 15, (h, w, 3)).astype(np.int16)
        texture = np.clip(texture.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        for _ in range(np.random.randint(2, 8))
            pt1 = (np.random.randint(0, w), np.random.randint(0, h))
            pt2 = (np.random.randint(0, w), np.random.randint(0, h))
            vein_color = base_color + np.random.randint(-40, 40)
            vein_color = max(0, min(255, vein_color))
            cv2.line(texture, pt1, pt2, (vein_color, vein_color, vein_color), 1)

        return texture

    def generate_single_image(
        self,
        fragmentation_quality str = mixed,
        n_fragments_range Tuple[int, int] = (15, 60),
    )
        h, w = self.image_size
        bg_color = np.random.randint(40, 70)
        image = np.full((h, w, 3), bg_color, dtype=np.uint8)
        mask = np.zeros((h, w), dtype=np.int32)

        if fragmentation_quality == fine
            mean_log, sigma_log = 2.0, 0.6
            n_range = (30, 60)
        elif fragmentation_quality == coarse
            mean_log, sigma_log = 3.5, 0.4
            n_range = (8, 20)
        elif fragmentation_quality == mixed
            mean_log, sigma_log = 2.8, 1.0
            n_range = (15, 40)
        else
            mean_log, sigma_log = 2.8, 0.8
            n_range = n_fragments_range

        n_fragments = np.random.randint(n_range[0], n_range[1])
        sizes = np.random.lognormal(mean=mean_log, sigma=sigma_log, size=n_fragments)
        max_size = min(h, w)  0.35
        sizes = np.clip(sizes, 3, max_size)

        fragment_id = 1
        placed_fragments = []

        sorted_indices = np.argsort(-sizes)
        for idx in sorted_indices
            size = sizes[idx]
            for attempt in range(50)
                cx = np.random.randint(int(size), int(w - size))
                cy = np.random.randint(int(size), int(h - size))

                overlap = False
                for pc, ps in placed_fragments
                    dist = np.sqrt((cx - pc[0])  2 + (cy - pc[1])  2)
                    if dist  (size + ps)  0.7
                        overlap = True
                        break

                if not overlap
                    break
            else
                continue

            vertices = self.generate_fragment(
                (cx, cy),
                size,
                irregularity=np.random.uniform(0.2, 0.5),
                spikiness=np.random.uniform(0.1, 0.3),
            )

            frag_mask = np.zeros((h, w), dtype=np.uint8)
            pts = np.array(vertices, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(frag_mask, [pts], 255)

            texture = self.generate_rock_texture(frag_mask)

            light_angle = np.random.uniform(0, 2  np.pi)
            gradient = np.zeros((h, w), dtype=np.float32)
            for y_pos in range(h)
                for x_pos in range(w)
                    gradient[y_pos, x_pos] = (
                        0.7
                        + 0.3
                         np.cos(light_angle)
                         (x_pos - cx)
                         max(size, 1)
                        + 0.3
                         np.sin(light_angle)
                         (y_pos - cy)
                         max(size, 1)
                    )
            gradient = np.clip(gradient, 0.4, 1.2)

            for c in range(3)
                textured = (texture[, , c]  gradient).astype(np.uint8)
                image[, , c] = np.where(frag_mask  0, textured, image[, , c])

            edge_kernel = np.ones((3, 3), np.uint8)
            edge = cv2.dilate(frag_mask, edge_kernel, iterations=1) - frag_mask
            shadow_color = max(0, bg_color - 30)
            for c in range(3)
                image[, , c] = np.where(
                    edge  0, shadow_color, image[, , c]
                )

            mask[frag_mask  0] = fragment_id
            placed_fragments.append(((cx, cy), size))
            fragment_id += 1

        noise = np.random.normal(0, 8, image.shape).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        pil_image = Image.fromarray(image)
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        image = np.array(pil_image)

        brightness_factor = np.random.uniform(0.7, 1.3)
        image = np.clip(image  brightness_factor, 0, 255).astype(np.uint8)

        return image, mask, {
            n_fragments fragment_id - 1,
            quality fragmentation_quality,
            sizes sizes.tolist(),
        }

    def generate_dataset(self, n_images int = 1000)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.masks_dir.mkdir(parents=True, exist_ok=True)

        metadata = []
        quality_distribution = {
            fine int(n_images  0.3),
            coarse int(n_images  0.3),
            mixed n_images - int(n_images  0.3)  2,
        }

        idx = 0
        for quality, count in quality_distribution.items()
            for _ in range(count)
                image, mask, info = self.generate_single_image(
                    fragmentation_quality=quality
                )

                img_filename = frock_{idx05d}.png
                mask_filename = fmask_{idx05d}.png

                cv2.imwrite(
                    str(self.images_dir  img_filename), cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                )

                binary_mask = (mask  0).astype(np.uint8)  255
                cv2.imwrite(str(self.masks_dir  mask_filename), binary_mask)

                info[image_file] = img_filename
                info[mask_file] = mask_filename
                info[index] = idx
                metadata.append(info)
                idx += 1

                if idx % 100 == 0
                    print(fGenerated {idx}{n_images} images...)

        with open(self.output_dir  metadata.json, w) as f
            json.dump(metadata, f, indent=2)

        print(fDataset generation complete {idx} images saved to {self.output_dir})
        return metadata
