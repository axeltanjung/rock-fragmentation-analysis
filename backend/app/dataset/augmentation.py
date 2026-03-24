import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random


def random_rotation(image: Image.Image, mask: Image.Image):
    angle = random.choice([0, 90, 180, 270])
    return image.rotate(angle), mask.rotate(angle, resample=Image.NEAREST)


def random_flip(image: Image.Image, mask: Image.Image):
    if random.random() > 0.5:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
    if random.random() > 0.5:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        mask = mask.transpose(Image.FLIP_TOP_BOTTOM)
    return image, mask


def random_brightness(image: Image.Image, mask: Image.Image, range_factor=(0.6, 1.4)):
    factor = random.uniform(*range_factor)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor), mask


def random_contrast(image: Image.Image, mask: Image.Image, range_factor=(0.7, 1.3)):
    factor = random.uniform(*range_factor)
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor), mask


def add_gaussian_noise(image: Image.Image, mask: Image.Image, sigma=15):
    img_array = np.array(image).astype(np.float32)
    noise = np.random.normal(0, sigma, img_array.shape)
    noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy), mask


def random_blur(image: Image.Image, mask: Image.Image, max_radius=2.0):
    radius = random.uniform(0, max_radius)
    return image.filter(ImageFilter.GaussianBlur(radius=radius)), mask


def augment_pair(image: Image.Image, mask: Image.Image):
    transforms = [
        random_rotation,
        random_flip,
        random_brightness,
        random_contrast,
        add_gaussian_noise,
        random_blur,
    ]
    random.shuffle(transforms)
    n_transforms = random.randint(2, len(transforms))
    for transform in transforms[:n_transforms]:
        image, mask = transform(image, mask)
    return image, mask
