# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') are not
# available if 'haveTK' below is False.  If you manage to install
# python-tk, you can set that to True.  Otherwise, you'll have to
# provide the filename in 'imgFilename' below.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component 
# of each pixel when doing intensity changes.

###### I'm using Python3 and adjusted the code to account for it


import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print( 'Error: Pillow has not been installed.' )
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)



haveTK = False # sys.platform != 'darwin'


# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if haveTK:
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()



# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast( brightness, contrast ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # YOUR CODE HERE

  # y component is brightness. Ergo, modifying brightness and contrast is modifying the y component - we don't want to change the colours 
  for x in range(width): 
    for y in range(height):
        dstPixels[x, y] = (int(contrast*srcPixels[x,y][0] + brightness),) + dstPixels[x, y][1:]

  print( 'adjust brightness = %f, contrast = %f' % (brightness,contrast) )


# Perform local histogram equalization on the current image using the given radius.
def performHistoEqualization( radius ):

  pixels = currentImage.load()
  width  = currentImage.size[0]
  height = currentImage.size[1]

  # YOUR CODE HERE
  # this still changes contrast, so only change the y component
  # save a copy of the y so it doesn't change throughout the function
  intensities = numpy.zeros((width, height))
  for x in range(width):
      for y in range(height):
          intensities[x, y] = pixels[x, y][0]
  for x in range(width):
      for y in range(height):
          # get neighbourhood coordinates
          minX = max(0, x - radius)
          maxX = min(width - 1, x + radius)
          minY = max(0, y - radius)
          maxY = min(height -1, y + radius)
          # n_at_most_pixel_inten is the number of pixels with at most intensity of the center pixel
          n_at_most_pixel_inten = 0 
          uniqueIntensities = [] # array holding the unique intensities (we want its length)
          minIntensity = 256 # minimum intensity
          # navigate through saved intensities and add to n_at_most_pixel_inten if it is less than the intensity of the centre pixel
          for hx in range(minX, maxX):
              for hy in range(minY, maxY):
                  if intensities[hx, hy] <= intensities[x,y]: 
                      n_at_most_pixel_inten += 1
                  if intensities[hx, hy] not in uniqueIntensities:
                      uniqueIntensities.append(intensities[hx, hy])
                  if intensities[hx, hy] < minIntensity:
                      minIntensity = intensities[hx, hy]
          # n_total_pixels is the number of pixels in the neighbourhood
          n_total_pixels = (maxX - minX)*(maxY - minY)
          # 256 is used as the N value, to distribute over 256 intensities
          pixels[x,y] = (int((256 / n_total_pixels) * n_at_most_pixel_inten - 1),) + pixels[x,y][1:]
          # the size of an array of unique intensities is used as the N value
          #pixels[x,y] = (int((len(uniqueIntensities) / n_total_pixels) * n_at_most_pixel_inten - 1),) + pixels[x,y][1:]
          # adding the minimum intensity
          # pixels[x,y] = (int(minIntensity + (len(uniqueIntensities) / n_total_pixels) * n_at_most_pixel_inten - 1),) + pixels[x,y][1:]

  print( 'perform local histogram equalization with radius %d' % radius )

# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage( factor ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # YOUR CODE HERE
  # backwards projection uses an inverse factor
  inverse = 1/factor
  # need to translate to center, scale, translate back
  # t_center = numpy.matrix([[1, 0, int(width/2)], [0, 1, int(height/2)], [0, 0, 1]])
  # t_scale = numpy.matrix([[factor, 0, 0], [0, factor, 0], [0, 0, factor]])
  # t_back_center = numpy.matrix([[1, 0, -int(width/2)], [0, 1, -int(height/2)], [0, 0, 1]])
  # t_final = numpy.linalg.inv((t_center.dot(t_scale)).dot(t_back_center))
  # print(t_final)
  for x in range(width):
      for y in range(height):
          # back projection coordinate
          x_back = x*inverse
          y_back = y*inverse
          # if outside image, set black
          if x_back >= width or y_back >= height:
              dstPixels[x, y] = (16, 128, 128)
          else: 
              dstPixels[x,y] = srcPixels[x_back, y_back]
  print( 'scale image by %f' % factor )

  

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = currentImage.convert( 'RGB' )

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( int(baseX), int(baseY) )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  global localHistoRadius

  if key == b'\033': # ESC = exit
    sys.exit(0)

  elif key == b'l':
    if haveTK:
      path = tkFileDialog.askopenfilename( initialdir = imgDir )
      if path:
        loadImage( path )

  elif key == b's':
    if haveTK:
      outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
      if outputPath:
        saveImage( outputPath )

  elif key == b'h':
    performHistoEqualization( localHistoRadius )

  elif key in ['+','=']:
    localHistoRadius = localHistoRadius + 1
    print( 'radius =', localHistoRadius )

  elif key in ['-','_']:
    localHistoRadius = localHistoRadius - 1
    if localHistoRadius < 1:
      localHistoRadius = 1
    print( 'radius =', localHistoRadius )

  else:
    print( 'key =', key )    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

  global currentImage

  currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


def saveImage( path ):

  global currentImage

  currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
  


# Handle window reshape


def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0



# Handle mouse click/release

def mouse( btn, state, x, y ):

  global button, initX, initY, tempImage

  if state == GLUT_DOWN:
    tempImage = currentImage.copy()
    button = btn
    initX = x
    initY = y
  elif state == GLUT_UP:
    tempImage = None
    button = None

  glutPostRedisplay()

  

# Handle mouse motion

def motion( x, y ):

  if button == GLUT_LEFT_BUTTON:

    diffX = x - initX
    diffY = y - initY

    applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

  elif button == GLUT_RIGHT_BUTTON:

    initPosX = initX - float(windowWidth)/2.0
    initPosY = initY - float(windowHeight)/2.0
    initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
    if initDist == 0:
      initDist = 1

    newPosX = x - float(windowWidth)/2.0
    newPosY = y - float(windowHeight)/2.0
    newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

    scaleImage( newDist / initDist )

  glutPostRedisplay()
  


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
