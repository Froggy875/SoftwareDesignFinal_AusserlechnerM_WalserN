import io
from PIL import Image

class ImageExporter:
    @staticmethod
    def fig_to_pil(fig):
        """Konvertiert eine Matplotlib-Figur in ein PIL-Image (fürs GIF)."""
        buf = io.BytesIO()
        # dpi=100 reicht für GIFs völlig aus und hält den Speicherbedarf gering
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        return Image.open(buf)

    @staticmethod
    def get_gif_bytes(frames, duration=200):
        """Erzeugt ein GIF aus einer Liste von PIL-Images und gibt es als Bytes zurück."""
        if not frames:
            return None
        buf = io.BytesIO()
        frames[0].save(
            buf,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=duration, # Anzeigedauer pro Frame in ms
            loop=0
        )
        return buf.getvalue()

    @staticmethod
    def get_image_bytes(fig):
        """Erzeugt ein hochauflösendes PNG aus einer Figur und gibt es als Bytes zurück."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        return buf.getvalue()