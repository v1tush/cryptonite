import segno

qrcode = segno.make_qr('Hello, World')

# потом доработаю
qrcode.save(
    'white_qrcode.png',
    scale=5,
    dark='white',  # цвет QR-кода
    light=None,  # прозрачный фон
)
