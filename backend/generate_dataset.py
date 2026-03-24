from app.dataset.generator import SyntheticRockDataset
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic rock fragmentation dataset")
    parser.add_argument("--n-images", type=int, default=1000)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--output-dir", default="data/synthetic")
    args = parser.parse_args()

    generator = SyntheticRockDataset(
        image_size=(args.image_size, args.image_size),
        output_dir=args.output_dir,
    )
    generator.generate_dataset(n_images=args.n_images)
