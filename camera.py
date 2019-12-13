import flirimageextractor
from matplotlib import cm

flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
flir.process_image('examples/ax8.jpg')
flir.save_images()
flir.plot()

