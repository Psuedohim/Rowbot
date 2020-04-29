#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>

#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

const int body_unit = 305;          // Farthest part of rover from scanner.
const int map_dim = 2048;           // Size of map in each dimension.
int base_point = (map_dim / 2) - 1; // Position of rover on map (1023, 1023).
bool env_map[map_dim][map_dim];     // Initialize map of type boolean.
std::vector<Point> Objects;
std::vector<Layer> Layers;
std::vector<Point> Steps;

struct Layer
{
  int r;
  bool occupied;
};

struct Circle
{
  int x = base_point; // Default starting point of circle.
  int y = base_point; // Default starting point of circle.
  int r = 180;        // Default radius of circle ~ half width of rover.
};

struct Point
{
  int x;
  int y;
  int r;
};

void init_layers()
{
  for (int i = 0; i < 4; i++)
  {
    Layer temp_layer;
    temp_layer.r = body_unit * std::pow(2, i);
    temp_layer.occupied = false;
    Layers.push_back(temp_layer);
  }
}

int scale_raw_distance(float distance)
{
  // Scale distance readings so that results can be mapped on fixed size grid.
  // Scales input from distance: [0, 5000] to result: [0, base_point]
  int max_distance = 5000; // Distance reading should never exceed 5000 mm.
  int result = (distance * base_point) / max_distance;
  return result;
}

Point vectorize_point(float theta, float distance)
{
  Point temp_point;
  temp_point.r = scale_raw_distance(distance);
  temp_point.x = temp_point.r * cos(theta);
  temp_point.y = temp_point.r * sin(theta);
  return temp_point;
}

void vectorize_scan(rplidar_response_measurement_node_hq_t nodes[8192], size_t count)
{
  for (int pos = 0; pos < (int)count; ++pos)
  {
    float angle = nodes[pos].angle_z_q14 * 90.f / (1 << 14); // Angle in degrees.
    float theta = (angle * 2 * 3.1416) / 360;                // Conversion to radians.
    float distance = nodes[pos].dist_mm_q2 / (1 << 2);
    Objects.push_back(vectorize_point(theta, distance));
  }
}

// void activate_layers(Point object)
// {
//   for (int i = 0; i < Layers.size(); i++)
//   {
//     if (std::isgreaterequal(object.r, Layers[i].r)) // If object is in layer.
//     {
//       Layers[i].occupied = true; // Activate layer.
//       return;                    // Stop searching through layers.
//     }
//   }
// };

struct activate_layers
{
  void operator()(Point &object)
  {
    for (int i = 0; i < Layers.size(); i++)
    {
      if (std::isgreaterequal(object.r, Layers[i].r)) // If object is in layer.
      {
        Layers[i].occupied = true; // Activate layer.
        return;                    // Stop searching through layers.
      }
    }
  }
};

int8_t calculate_speed()
{
  std::for_each(Objects.begin(), Objects.end(), activate_layers());
  for (int i = 0; i < Layers.size(); i++)
  {
    if (Layers[i].occupied) 
  }
}

bool inside_circle(Circle circle, Point point)
{
  int dx = circle.x - point.x;
  int dy = circle.y - point.y;
  if ((std::pow(dx, 2) + std::pow(dy, 2)) <= std::pow(circle.r, 2))
    return true;
  else
    return false;
}

void navigator()
{
  // Return set of steps to assigned goal point.
  std::queue<int[2]> steps;
}

int main()
{
}
