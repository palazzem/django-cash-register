import pytest

from io import BytesIO

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile


@pytest.fixture
def temp_image():
    """
    Creates an empty in-memory image that is uploaded as
    a Django ``InMemoryUploadedFile``. This fixture can be
    used in DRF serializers when a fake image is required.
    """
    # create an in-memory bytes stream
    memory_fp = BytesIO()
    # create an empty RGB image
    image = Image.new('RGB', (1, 1))
    image.save(memory_fp, format='PNG')
    # use an in-memory uploaded file
    image_file = InMemoryUploadedFile(
        memory_fp,
        field_name='tempfile',
        name='tempfile.png',
        content_type='image/png',
        size=len(memory_fp.getvalue()),
        charset='utf-8',
    )
    # return the image
    image_file.seek(0)
    return image_file
