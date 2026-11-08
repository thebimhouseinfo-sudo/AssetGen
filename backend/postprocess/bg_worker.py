"""Standalone background-removal worker (BiRefNet).

Runs in an external interpreter that has torch + transformers installed.
It deliberately imports nothing from AssetGen. Writes an RGBA PNG.
"""
import argparse
import sys


def pick_device(torch, requested):
    if requested:
        return requested
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Remove image background with BiRefNet")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="ZhengPeng7/BiRefNet")
    parser.add_argument("--device", default=None, choices=["mps", "cpu"])
    args = parser.parse_args(argv)

    import torch
    from PIL import Image
    from torchvision import transforms
    from transformers import AutoModelForImageSegmentation

    device = pick_device(torch, args.device)
    model = AutoModelForImageSegmentation.from_pretrained(args.model, trust_remote_code=True)
    model.to(device).eval()

    transform = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    with Image.open(args.input) as src:
        image = src.convert("RGB")
    batch = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        pred = model(batch)[-1].sigmoid().cpu()[0].squeeze()
    mask = transforms.ToPILImage()(pred).resize(image.size, Image.Resampling.LANCZOS)
    image.putalpha(mask)
    image.save(args.output, format="PNG")
    return 0


if __name__ == "__main__":
    sys.exit(main())
