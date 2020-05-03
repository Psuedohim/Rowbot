#include "header.h"

struct Layer
{
  int r;
  bool occupied;
};

struct Circle
{
  int x;
  int y;
  int r;  // Radius of circle.
};

struct Point
{
  int x;
  int y;
  int r = -1;  // Radius of point from origin.
};

bool inside_circle(Circle, std::vector<Point>);