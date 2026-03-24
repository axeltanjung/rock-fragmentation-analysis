import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path

from app.models.unet import UNet
from app.dataset.generator import SyntheticRockDataset
from app.dataset.augmentation import augment_pair


class RockSegmentationDataset(Dataset):
    def __init__(self, images_dir, masks_dir, image_size=(256, 256), augment=True):
        self.images_dir = Path(images_dir)
        self.masks_dir = Path(masks_dir)
        self.image_size = image_size
        self.augment = augment

        self.image_files = sorted(self.images_dir.glob("*.png"))
        self.mask_files = sorted(self.masks_dir.glob("*.png"))

        assert len(self.image_files) == len(self.mask_files), (
            f"Image count ({len(self.image_files)}) != mask count ({len(self.mask_files)})"
        )

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image = Image.open(self.image_files[idx]).convert("RGB")
        mask = Image.open(self.mask_files[idx]).convert("L")

        if self.augment:
            image, mask = augment_pair(image, mask)

        image = image.resize(self.image_size, Image.BILINEAR)
        mask = mask.resize(self.image_size, Image.NEAREST)

        img_array = np.array(image).astype(np.float32) / 255.0
        mask_array = (np.array(mask) > 127).astype(np.float32)

        img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1))
        mask_tensor = torch.from_numpy(mask_array).unsqueeze(0)

        return img_tensor, mask_tensor


class DiceLoss(nn.Module):
    def __init__(self, smooth=1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, pred, target):
        pred = torch.sigmoid(pred)
        pred_flat = pred.view(-1)
        target_flat = target.view(-1)
        intersection = (pred_flat * target_flat).sum()
        return 1 - (2.0 * intersection + self.smooth) / (
            pred_flat.sum() + target_flat.sum() + self.smooth
        )


class CombinedLoss(nn.Module):
    def __init__(self, bce_weight=0.5, dice_weight=0.5):
        super().__init__()
        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

    def forward(self, pred, target):
        return self.bce_weight * self.bce(pred, target) + self.dice_weight * self.dice(
            pred, target
        )


def train(
    data_dir="data/synthetic",
    output_dir="models",
    epochs=50,
    batch_size=8,
    learning_rate=1e-3,
    image_size=256,
    device=None,
):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    print(f"Training on: {device}")

    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not (data_path / "images").exists():
        print("Generating synthetic dataset...")
        generator = SyntheticRockDataset(
            image_size=(image_size, image_size), output_dir=data_dir
        )
        generator.generate_dataset(n_images=1000)

    dataset = RockSegmentationDataset(
        images_dir=data_path / "images",
        masks_dir=data_path / "masks",
        image_size=(image_size, image_size),
        augment=True,
    )

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    val_dataset.dataset.augment = False

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
    )

    model = UNet(n_channels=3, n_classes=1, bilinear=False).to(device)
    criterion = CombinedLoss(bce_weight=0.5, dice_weight=0.5)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    best_val_loss = float("inf")
    patience_counter = 0
    max_patience = 10

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_idx, (images, masks) in enumerate(train_loader):
            images = images.to(device)
            masks = masks.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        model.eval()
        val_loss = 0.0
        val_dice = 0.0
        with torch.no_grad():
            for images, masks in val_loader:
                images = images.to(device)
                masks = masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()

                preds = (torch.sigmoid(outputs) > 0.5).float()
                intersection = (preds * masks).sum()
                dice = (2 * intersection + 1) / (preds.sum() + masks.sum() + 1)
                val_dice += dice.item()

        val_loss /= len(val_loader)
        val_dice /= len(val_loader)
        scheduler.step(val_loss)

        current_lr = optimizer.param_groups[0]["lr"]
        print(
            f"Epoch {epoch + 1}/{epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Dice: {val_dice:.4f} | "
            f"LR: {current_lr:.6f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), output_path / "best_model.pth")
            patience_counter = 0
            print(f"  -> Saved best model (val_loss={val_loss:.4f})")
        else:
            patience_counter += 1

        if patience_counter >= max_patience:
            print(f"Early stopping at epoch {epoch + 1}")
            break

        if (epoch + 1) % 10 == 0:
            torch.save(
                model.state_dict(), output_path / f"model_epoch_{epoch + 1}.pth"
            )

    torch.save(model.state_dict(), output_path / "final_model.pth")
    print(f"Training complete. Best val_loss: {best_val_loss:.4f}")
    return model


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train U-Net for rock segmentation")
    parser.add_argument("--data-dir", default="data/synthetic")
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    train(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        image_size=args.image_size,
        device=args.device,
    )
