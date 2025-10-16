import io
import os
from django.conf import settings
from PIL import Image
import fitz  # pymupdf
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import hashlib

THUMB_MAX_SIZE = (300, 300)  # size max of the miniature

def _ensure_dir(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)

def make_image_thumbnail(filefield, dest_path):
    """"Generates thumbnail for image (jpg/png), returns relative path within MEDIA_ROOT."
    # filefield can be a FieldFile (File.file)"""
    fileobj = filefield
    fileobj.open()
    img = Image.open(fileobj)
    img.convert("RGB")
    img.thumbnail(THUMB_MAX_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=75)
    buf.seek(0)
    _ensure_dir(os.path.join(settings.MEDIA_ROOT, dest_path))
    saved_path = default_storage.save(dest_path, ContentFile(buf.read()))
    fileobj.close()
    return saved_path

def make_pdf_thumbnail(filefield, dest_path):
    """Generate thumbnail of the first page of the PDF using PyMuPDF."""
    fileobj = filefield
    fileobj.open()
    # leer bytes
    pdf_bytes = fileobj.read()
    fileobj.close()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)  # first page
    mat = fitz.Matrix(2, 2)  # adjust resolution (2x)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("ppm")
    img = Image.open(io.BytesIO(img_bytes))
    img.convert("RGB")
    img.thumbnail(THUMB_MAX_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=75)
    buf.seek(0)

    _ensure_dir(os.path.join(settings.MEDIA_ROOT, dest_path))
    saved_path = default_storage.save(dest_path, ContentFile(buf.read()))
    return saved_path

def generate_thumbnail_for_file(file_instance):
    """
    Detects type and generates thumbnail; returns URL (relative to MEDIA) or None.
    in this function we will to get the image or file that the user need make his miniature
    """
    if not file_instance.file:
        return None

    # Unique name for thumbnail based on id/filename/hash
    fname = getattr(file_instance.file, 'name', 'file')
    key = f"{file_instance.id}_{fname}"
    h = hashlib.sha1(key.encode()).hexdigest()
    thumb_rel_path = f"thumbnails/{h}.jpg"

    # If it already exists in storage, return it
    if default_storage.exists(thumb_rel_path):
        return default_storage.url(thumb_rel_path)

    # Determine extension
    lower = fname.lower()
    try:
        if lower.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            path = make_image_thumbnail(file_instance.file, thumb_rel_path)
        elif lower.endswith('.pdf'):
            path = make_pdf_thumbnail(file_instance.file, thumb_rel_path)
        else:
            # here for (docx/xls, etc) we will use a icon
            return None
    except Exception as e:
        # log error in production
        return None

    return default_storage.url(path)
