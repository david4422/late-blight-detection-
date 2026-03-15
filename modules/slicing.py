from PIL import Image


def slice_image(image, patch_w, patch_h):
    """Cut an image into patches of given size."""
    w, h = image.size
    cols_count = -(-w // patch_w)
    rows_count = -(-h // patch_h)

    patches = []
    for row in range(rows_count):
        for col in range(cols_count):
            x = min(col * patch_w, w - patch_w)
            y = min(row * patch_h, h - patch_h)
            patch = image.crop((x, y, x + patch_w, y + patch_h))
            patches.append({"image": patch, "row": row, "col": col, "x": x, "y": y})

    return patches, cols_count, rows_count
