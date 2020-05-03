#include "geometry.h"

bool inside_circle(Circle circle, std::vector<Point> objects)
{
  for (int i = 0; i < objects.size(); i++)
  {
  Point object = objects[i];
  int dx = circle.x - object.x;
  int dy = circle.y - object.y;
  if ((std::pow(dx, 2) + std::pow(dy, 2)) <= std::pow(circle.r, 2))
    return true;
  }
  return false;
}
