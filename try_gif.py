# Requires: pip install pillow
import os
import re
import glob
from typing import List, Optional, Tuple
from PIL import Image

def natural_sort_key(s: str):
    # Sorts strings with numbers in human order: img1.png, img2.png, img10.png
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def collect_image_paths(input_dir: str, patterns: Tuple[str, ...] = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.webp')) -> List[str]:
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(os.path.join(input_dir, pat)))
    return sorted(paths, key=natural_sort_key)

def fit_to_canvas(img: Image.Image, size: Tuple[int, int], keep_aspect: bool = True, bgcolor=(0, 0, 0, 0)) -> Image.Image:
    """Resize and/or pad image to exactly match size."""
    target_w, target_h = size
    if keep_aspect:
        # Maintain aspect ratio and letterbox
        w, h = img.size
        scale = min(target_w / w, target_h / h)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new('RGBA', (target_w, target_h), bgcolor)
        offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
        canvas.paste(img, offset)
        return canvas
    else:
        # Force resize ignoring aspect
        return img.resize(size, Image.LANCZOS)

def load_frames(paths: List[str], target_size: Optional[Tuple[int, int]] = None) -> List[Image.Image]:
    frames = []
    base_size = None
    for i, p in enumerate(paths):
        img = Image.open(p).convert('RGBA')
        if i == 0:
            base_size = target_size or img.size
        # Normalize every frame to the same canvas size
        img = fit_to_canvas(img, base_size, keep_aspect=True, bgcolor=(0, 0, 0, 0))
        frames.append(img)
    return frames

def save_gif(frames: List[Image.Image], output_path: str, duration_ms: int = 100, loop: int = 0, optimize: bool = True):
    if not frames:
        raise ValueError("No frames to save.")
    # Convert frames to palette-based for GIF. Using adaptive palette per frame.
    # Pillow will handle quantization; disposal=2 ensures each frame replaces the previous.
    pal_frames = [f.convert('P', palette=Image.ADAPTIVE, colors=256) for f in frames]
    pal_frames[0].save(
        output_path,
        save_all=True,
        append_images=pal_frames[1:],
        format='GIF',
        duration=duration_ms,
        loop=loop,
        optimize=optimize,
        disposal=2,
    )

def make_gif_from_folder(
    input_dir: str,
    output_gif: str = "output.gif",
    fps: Optional[float] = None,
    duration_ms: Optional[int] = None,
    size: Optional[Tuple[int, int]] = None,
    loop: int = 0,
):
    paths = collect_image_paths(input_dir)
    print(paths)
    if not paths:
        raise FileNotFoundError(f"No images found in {input_dir}")
    # Determine duration from fps if provided
    if fps is not None and fps > 0:
        duration_ms = int(1000 / fps)
    if duration_ms is None:
        duration_ms = 100  # default 10 fps
    frames = load_frames(paths, target_size=size)
    save_gif(frames, output_gif, duration_ms=duration_ms, loop=loop)
    print(f"Saved GIF with {len(frames)} frames to {output_gif}")

if __name__ == "__main__":
    # Example usage without argparse; edit values below or wrap with argparse if desired.
    folder = "test_images1"   # change to your folder
    output = "animation1.gif"         # change to your desired output path
    # Either set fps (frames per second) or duration_ms (milliseconds per frame)
    make_gif_from_folder(
        input_dir=folder,
        output_gif=output,
        duration_ms=500,
        # fps=1,             # or set duration_ms=83
        size=(352, 371),    # set None to keep first image size; else all frames will be letterboxed to this size
        loop=0,             # 0 = infinite loop; set e.g. 1 to play once
    )

    folder = "test_images2"   # change to your folder
    output = "animation2.gif"         # change to your desired output path
    # Either set fps (frames per second) or duration_ms (milliseconds per frame)
    make_gif_from_folder(
        input_dir=folder,
        output_gif=output,
        duration_ms=500,
        # fps=1,             # or set duration_ms=83
        size=(352, 371),    # set None to keep first image size; else all frames will be letterboxed to this size
        loop=0,             # 0 = infinite loop; set e.g. 1 to play once
    )