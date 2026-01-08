#!/usr/bin/env python3
"""
Profile Photo Processor

Processes portrait photos by:
1. Removing background and replacing with #e1e1e1
2. Detecting face and centering it in the output
3. Normalizing brightness if needed
4. Outputting standardized JPEG

Requirements:
    pip install rembg pillow opencv-python numpy

Usage:
    python process_profile_photo.py input.jpg output.jpg [--size 1000] [--bg-color e1e1e1]
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove, new_session


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

    # Load face cascade
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

    # Return the largest face
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    return tuple(largest_face)


def refine_mask(mask: Image.Image, iterations: int = 2) -> Image.Image:
    """
    Refine the alpha mask to reduce jagged edges.
    Apply slight blur then threshold to get cleaner edges.
    """
    # Convert to numpy
    mask_array = np.array(mask)

    # Apply morphological operations to clean up edges
    kernel = np.ones((3, 3), np.uint8)

    # Close small holes
    mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    # Open to remove small noise
    mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_OPEN, kernel, iterations=1)

    # Apply slight Gaussian blur for smoother edges
    mask_array = cv2.GaussianBlur(mask_array, (3, 3), 0)

    # Threshold to make edges sharper (but not too harsh)
    _, mask_array = cv2.threshold(mask_array, 127, 255, cv2.THRESH_BINARY)

    return Image.fromarray(mask_array)


def normalize_brightness(image: Image.Image, min_brightness: float = 0.45) -> Image.Image:
    """
    Normalize image brightness - only brighten dark images, never darken.
    min_brightness: Minimum acceptable brightness (0.0-1.0), default 0.45
    """
    # Convert to grayscale to measure brightness
    grayscale = image.convert('L')
    histogram = grayscale.histogram()

    # Calculate current average brightness (0-255 scale)
    pixels = sum(histogram)
    brightness_sum = sum(i * histogram[i] for i in range(256))
    current_brightness = brightness_sum / pixels / 255.0

    print(f"Current brightness: {current_brightness:.3f}")

    # Only brighten if too dark (never darken)
    if current_brightness < min_brightness:
        if current_brightness > 0.01:  # Avoid division by zero
            factor = min_brightness / current_brightness
            # Clamp factor to reasonable range (only brighten, max 1.5x)
            factor = min(1.5, factor)
            print(f"Brightening by factor: {factor:.2f}")
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(factor)
    else:
        print("Image brightness is sufficient, skipping adjustment")

    return image


def process_profile_photo(
    input_path: str,
    output_path: str,
    output_size: int = 1000,
    bg_color: str = "e1e1e1",
    face_ratio: float = 0.18,
    face_vertical_position: float = 0.42,
    normalize: bool = True,
    model: str = "isnet-general-use"
) -> None:
    """
    Process a profile photo.

    Args:
        input_path: Path to input image
        output_path: Path to output image
        output_size: Maximum dimension of output image (default: 1000)
        bg_color: Background color in hex (default: e1e1e1)
        face_ratio: Target ratio of face height to image height (default: 0.15)
        face_vertical_position: Vertical position of face center (0=top, 1=bottom, default: 0.30)
        normalize: Whether to normalize brightness (default: True)
        model: rembg model to use (default: isnet-general-use for better quality)
    """
    # Load image
    input_image = Image.open(input_path).convert('RGBA')

    # Convert to numpy for face detection (before background removal)
    rgb_array = np.array(input_image.convert('RGB'))

    # Detect face first
    print("Detecting face...")
    face = detect_face(rgb_array)

    if face is None:
        print("Warning: No face detected. Centering image as-is.")
        face_center_x = rgb_array.shape[1] // 2
        face_center_y = rgb_array.shape[0] // 3
        face_height = rgb_array.shape[0] // 4
    else:
        x, y, w, h = face
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        face_height = h
        print(f"Face detected at: ({x}, {y}), size: {w}x{h}")

    # Remove background using rembg with specified model
    print(f"Removing background (model: {model})...")
    session = new_session(model)
    removed_bg = remove(
        input_image,
        session=session,
        post_process_mask=True,  # Enable post-processing for cleaner edges
    )

    # Refine the alpha mask for cleaner edges
    print("Refining edges...")
    if removed_bg.mode == 'RGBA':
        r, g, b, a = removed_bg.split()
        refined_alpha = refine_mask(a)
        removed_bg = Image.merge('RGBA', (r, g, b, refined_alpha))

    # Calculate scaling to achieve target face ratio
    target_face_height = output_size * face_ratio
    scale = target_face_height / face_height if face_height > 0 else 1.0

    # Scale the image
    new_width = int(removed_bg.width * scale)
    new_height = int(removed_bg.height * scale)
    scaled_image = removed_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Update face center coordinates after scaling
    scaled_face_center_x = int(face_center_x * scale)
    scaled_face_center_y = int(face_center_y * scale)

    # Create output canvas with background color
    bg_rgb = hex_to_rgb(bg_color)

    # Calculate output dimensions
    # Use the original aspect ratio but ensure it fits within output_size
    aspect_ratio = input_image.width / input_image.height

    if aspect_ratio < 1:  # Portrait
        out_width = int(output_size * aspect_ratio)
        out_height = output_size
    else:  # Landscape or square
        out_width = output_size
        out_height = int(output_size / aspect_ratio)

    # Ensure minimum dimensions
    out_width = max(out_width, int(output_size * 0.6))
    out_height = max(out_height, output_size)

    # Create canvas
    canvas = Image.new('RGBA', (out_width, out_height), (*bg_rgb, 255))

    # Calculate position to place face at target vertical position
    target_face_y = int(out_height * face_vertical_position)
    target_face_x = out_width // 2

    paste_x = target_face_x - scaled_face_center_x
    paste_y = target_face_y - scaled_face_center_y

    # Paste the scaled image onto canvas
    canvas.paste(scaled_image, (paste_x, paste_y), scaled_image)

    # Convert to RGB for JPEG output
    output_image = Image.new('RGB', canvas.size, bg_rgb)
    output_image.paste(canvas, mask=canvas.split()[3])

    # Normalize brightness if requested (only brighten dark images)
    if normalize:
        print("Checking brightness...")
        output_image = normalize_brightness(output_image, min_brightness=0.40)

    # Save as JPEG
    print(f"Saving to {output_path}...")
    output_image.save(output_path, 'JPEG', quality=95)
    print("Done!")


def main():
    parser = argparse.ArgumentParser(
        description='Process profile photos: remove background, center face, normalize brightness'
    )
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output image path')
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

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    process_profile_photo(
        args.input,
        args.output,
        output_size=args.size,
        bg_color=args.bg_color,
        face_ratio=args.face_ratio,
        face_vertical_position=args.face_position,
        normalize=not args.no_normalize,
        model=args.model
    )


if __name__ == '__main__':
    main()
