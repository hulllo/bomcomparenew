from PIL import Image
filename = r'bomicon.png'
img = Image.open(filename)
img.save('logo.ico')