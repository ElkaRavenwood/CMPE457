// convolve.cpp

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <cstring>
using namespace std;

float outputScale = 1;

float lookup( float *a, int x, int y, int xdim, int ydim )

{
  if (x < 0 || x >= xdim || y < 0 || y >= ydim)
    return 0;

  return a[x+y*xdim];
}


void readFilter( char *filename, int &xdim, int &ydim, float * &a )

{
  float scale;

  if (filename[0] == '-' && filename[1] == '\0') {

    // read from stin

    cin >> xdim >> ydim >> scale;

    a = new float[ xdim*ydim ];

    for (int i=0; i<xdim*ydim; i++)
      cin >> a[i];

  } else {

    // read from file

    ifstream in( filename );

    in >> xdim >> ydim >> scale;

    a = new float[ xdim*ydim ];

    for (int i=0; i<xdim*ydim; i++)
      in >> a[i];
  }

  outputScale *= scale;
}


float *a, *b;			// two filters
int ax, ay, bx, by;		// filter dimensions

bool gnuplot = false;		// if true, output for plotting with gnuplot


int main( int argc, char **argv )

{
  int argIndex = 1;

  // Get options

  if (argc > 1 && strcmp( argv[1], "-gnuplot" ) == 0) {
    gnuplot = true;
    argIndex++;
  }
    
  if (argc < 2 + argIndex) {
    cerr << "Usage: " << argv[0] << " [-gnuplot] filter1 filter2" << endl;
    return 1;
  }

  // Read the filters

  readFilter( argv[argIndex], ax, ay, a );
  readFilter( argv[argIndex+1], bx, by, b );

  // Do the convolution

  int rx = ax + (bx-1);
  int ry = ay + (by-1);

  float *r = new float[rx*ry];

  int k=0;
  for (int y=0; y<ry; y++)
    for (int x=0; x<rx; x++) {
      float sum = 0;
      for (int i=0; i<ax; i++)
	for (int j=0; j<ay; j++)
	  sum += lookup(a,i,j,ax,ay) * lookup(b,x-i,y-j,bx,by);
      r[k++] = sum;
    }

  // Output

  if (!gnuplot) {

    // Output as a filter

    // Find the max width entry (for aligned columns upon output)

    int maxWidth = 0;

    for (int i=0; i<rx*ry; i++) {
      stringstream stream;
      stream << r[i];
      int width = stream.str().length();
      if (width > maxWidth)
	maxWidth = width;
    }

    // Output the result

    cout << rx << " " << ry << endl;

    cout << outputScale << endl;

    k = 0;

    for (int j=0; j<ry; j++) {
      for (int i=0; i<rx; i++)
	cout << setw( maxWidth+1 ) << r[k++];
      cout << endl;
    }

  } else {

    // Output for plotting with gnuplot

    k = 0;

    for (int j=0; j<ry; j++)
      for (int i=0; i<rx; i++)
	if (rx == 1)
	  cout << j << " " << r[k++]*outputScale << endl;
	else if (ry == 1)
	  cout << i << " " << r[k++]*outputScale << endl;
	else
	  cout << i << " " << j << " " << r[k++]*outputScale << endl;
  }

  return 0;
}
