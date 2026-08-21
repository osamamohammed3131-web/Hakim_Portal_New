import io, qrcode
def make_qr_bytes(url):
    q=qrcode.QRCode(box_size=8,border=2); q.add_data(url); q.make(fit=True)
    b=io.BytesIO(); q.make_image().save(b,format="PNG"); return b.getvalue()
