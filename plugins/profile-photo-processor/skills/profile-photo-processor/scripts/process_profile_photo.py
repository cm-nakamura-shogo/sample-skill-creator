#!/usr/bin/env python3
"""
Profile Photo Processor

Processes portrait photos by:
1. Removing background and replacing with #e1e1e1
2. Detecting face and centering it in the output
3. Normalizing brightness if needed
4. Outputting standardized JPEG

Supports both single file and folder processing.

Usage:
    # Single file
    python process_profile_photo.py input.jpg output.jpg

    # Folder processing
    python process_profile_photo.py input_folder/ output_folder/
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove, new_session


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def detect_face(image: np.ndarray) -> tuple[int, int, int, int] | None:
    """
    Detect face in image using OpenCV's Haar Cascade.
    Returns (x, y, w, h) of the largest face or None if no face detected.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) == 0:
        return None

    largest_face = max(faces, key=lambda f: f[2] * f[3])
    return tuple(largest_face)


def refine_mask(mask: Image.Image, iterations: int = 2) -> Image.Image:
    """Refine the alpha mask to reduce jagged edges."""
    mask_array = np.array(mask)

    kernel = np.ones((3, 3), np.uint8)
    mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_array = cv2.GaussianBlur(mask_array, (3, 3), 0)
    _, mask_array = cv2.threshold(mask_array, 127, 255, cv2.THRESH_BINARY)

    return Image.fromarray(mask_array)


def normalize_brightness(image: Image.Image, min_brightness: float = 0.45) -> Image.Image:
    """Normalize image brightness - only brighten dark images, never darken."""
    grayscale = image.convert('L')
    histogram = grayscale.histogram()

    pixels = sum(histogram)
    brightness_sum = sum(i * histogram[i] for i in range(256))
    current_brightness = brightness_sum / pixels / 255.0

    print(f"  Current brightness: {current_brightness:.3f}")

    if current_brightness < min_brightness:
        if current_brightness > 0.01:
            factor = min(1.5, min_brightness / current_brightness)
            print(f"  Brightening by factor: {factor:.2f}")
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(factor)
    else:
        print("  Brightness OK, skipping adjustment")

    return image


def process_single_photo(
    input_path: Path,
    output_path: Path,
    session,
    output_size: int = 1000,
    bg_color: str = "e1e1e1",
    face_ratio: float = 0.18,
    face_vertical_position: float = 0.42,
    normalize: bool = True,
) -> bool:
    """Process a single profile photo. Returns True on success."""
    try:
        print(f"Processing: {input_path.name}")

        input_image = Image.open(input_path).convert('RGBA')
        rgb_array = np.array(input_image.convert('RGB'))

        # Detect face
        print("  Detecting face...")
        face = detect_face(rgb_array)

        if face is None:
            print("  Warning: No face detected. Centering image as-is.")
            face_center_x = rgb_array.shape[1] // 2
            face_center_y = rgb_array.shape[0] // 3
            face_height = rgb_array.shape[0] // 4
        else:
            x, y, w, h = face
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            face_height = h
            print(f"  Face detected at: ({x}, {y}), size: {w}x{h}")

        # Remove background
        print("  Removing background...")
        removed_bg = remove(
            input_image,
            session=session,
            post_process_mask=True,
        )

        # Refine edges
        if removed_bg.mode == 'RGBA':
            r, g, b, a = removed_bg.split()
            refined_alpha = refine_mask(a)
            removed_bg = Image.merge('RGBA', (r, g, b, refined_alpha))

        # Calculate scaling
        target_face_height = output_size * face_ratio
        scale = target_face_height / face_height if face_height > 0 else 1.0

        new_width = int(removed_bg.width * scale)
        new_height = int(removed_bg.height * scale)
        scaled_image = removed_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        scaled_face_center_x = int(face_center_x * scale)
        scaled_face_center_y = int(face_center_y * scale)

        # Create canvas
        bg_rgb = hex_to_rgb(bg_color)
        aspect_ratio = input_image.width / input_image.height

        if aspect_ratio < 1:
            out_width = int(output_size * aspect_ratio)
            out_height = output_size
        else:
            out_width = output_size
            out_height = int(output_size / aspect_ratio)

        out_width = max(out_width, int(output_size * 0.6))
        out_height = max(out_height, output_size)

        canvas = Image.new('RGBA', (out_width, out_height), (*bg_rgb, 255))

        target_face_y = int(out_height * face_vertical_position)
        target_face_x = out_width // 2

        paste_x = target_face_x - scaled_face_center_x
        paste_y = target_face_y - scaled_face_center_y

        canvas.paste(scaled_image, (paste_x, paste_y), scaled_image)

        output_image = Image.new('RGB', canvas.size, bg_rgb)
        output_image.paste(canvas, mask=canvas.split()[3])

        if normalize:
            output_image = normalize_brightness(output_image, min_brightness=0.40)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_image.save(output_path, 'JPEG', quality=95)
        print(f"  Saved: {output_path}")
        return True

    except Exception as e:
        print(f"  Error processing {input_path.name}: {e}", file=sys.stderr)
        return False


def process_folder(
    input_dir: Path,
    output_dir: Path,
    **kwargs
) -> tuple[int, int]:
    """Process all images in a folder. Returns (success_count, fail_count)."""
    # Initialize session once for all images
    model = kwargs.pop('model', 'isnet-general-use')
    print(f"Initializing model: {model}")
    session = new_session(model)

    # Find all image files
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not image_files:
        print(f"No image files found in {input_dir}")
        return 0, 0

    print(f"Found {len(image_files)} image(s) to process\n")

    success_count = 0
    fail_count = 0

    for input_path in sorted(image_files):
        output_path = output_dir / f"{input_path.stem}.jpg"

        if process_single_photo(input_path, output_path, session, **kwargs):
            success_count += 1
        else:
            fail_count += 1
        print()

    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description='Process profile photos: remove background, center face, normalize brightness. '
                    'Supports single file or folder processing.'
    )
    parser.add_argument('input', help='Input image file or folder')
    parser.add_argument('output', help='Output image file or folder')
    parser.add_argument(
        '--size', type=int, default=1000,
        help='Maximum output dimension (default: 1000)'
    )
    parser.add_argument(
        '--bg-color', default='e1e1e1',
        help='Background color in hex (default: e1e1e1)'
    )
    parser.add_argument(
        '--face-ratio', type=float, default=0.18,
        help='Target ratio of face height to image height (default: 0.18)'
    )
    parser.add_argument(
        '--face-position', type=float, default=0.42,
        help='Vertical position of face (0=top, 1=bottom, default: 0.42)'
    )
    parser.add_argument(
        '--model', default='isnet-general-use',
        choices=['u2net', 'u2netp', 'u2net_human_seg', 'isnet-general-use', 'isnet-anime'],
        help='Background removal model (default: isnet-general-use)'
    )
    parser.add_argument(
        '--no-normalize', action='store_true',
        help='Skip brightness normalization'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    common_args = {
        'output_size': args.size,
        'bg_color': args.bg_color,
        'face_ratio': args.face_ratio,
        'face_vertical_position': args.face_position,
        'normalize': not args.no_normalize,
        'model': args.model,
    }

    if input_path.is_dir():
        # Folder processing
        print(f"=== Folder Processing Mode ===")
        print(f"Input folder: {input_path}")
        print(f"Output folder: {output_path}\n")

        output_path.mkdir(parents=True, exist_ok=True)

        success, fail = process_folder(input_path, output_path, **common_args)

        print(f"=== Summary ===")
        print(f"Success: {success}")
        print(f"Failed: {fail}")

        if fail > 0:
            sys.exit(1)
    else:
        # Single file processing
        print(f"=== Single File Mode ===")
        session = new_session(args.model)
        common_args.pop('model')

        if not process_single_photo(input_path, output_path, session, **common_args):
            sys.exit(1)

    print("\nDone!")


if __name__ == '__main__':
    main()
