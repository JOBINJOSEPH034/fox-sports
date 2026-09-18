import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from cloudinary_storage.storage import MediaCloudinaryStorage


class CustomMediaStorage(MediaCloudinaryStorage):
    """
    Intelligent Media Storage for JoLetics / Fox Sports:
    1. Prevents double-prefixing if an ImageField stores a full URL (http/https).
    2. Uses Cloudinary CDN if API credentials are fully configured.
    3. Seamlessly falls back to Whitenoise-served static files (/static/...) for pre-bundled images.
    """

    def url(self, name):
        if not name:
            return ''

        name_str = str(name).strip()

        # 1. If it's already an absolute URL, return directly (prevents double-encoding)
        if name_str.startswith('http://') or name_str.startswith('https://'):
            return name_str

        # 2. Check if Cloudinary credentials are configured
        cloudinary_conf = getattr(settings, 'CLOUDINARY_STORAGE', {})
        has_cloudinary_keys = bool(
            cloudinary_conf.get('API_KEY') and cloudinary_conf.get('API_SECRET')
        )

        if has_cloudinary_keys:
            try:
                c_url = super().url(name)
                # Safeguard against any double-prefixing
                if 'https:/res.cloudinary.com' in c_url and c_url.count('http') > 1:
                    idx = c_url.rfind('http')
                    return c_url[idx:]
                return c_url
            except Exception:
                pass

        # 3. Static / Whitenoise Fallback
        # Clean relative path like "product_images/shoe.jpg"
        clean_name = name_str.lstrip('/').replace('\\', '/')
        return f"{settings.STATIC_URL}{clean_name}"

    def _save(self, name, content):
        cloudinary_conf = getattr(settings, 'CLOUDINARY_STORAGE', {})
        has_cloudinary_keys = bool(
            cloudinary_conf.get('API_KEY') and cloudinary_conf.get('API_SECRET')
        )
        if has_cloudinary_keys:
            try:
                return super()._save(name, content)
            except Exception:
                pass
        # Fallback to standard filesystem storage if Cloudinary upload fails / credentials not set
        fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
        return fs._save(name, content)
