from django.utils.text import slugify as url_slugify


def slugify(text):
    """
    Returns a slug using underscores instead of dashes.
    """
    return url_slugify(text).replace('-', '_')
