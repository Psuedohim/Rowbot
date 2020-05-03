#include <valarray> // Lib for element-wise operations.
#include "geometry.h"
#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

const int body_unit = 305;          // Farthest part of rover from scanner.
const int map_dim = 2048;           // Size of map in each dimension.
int base_point = (map_dim / 2) - 1; // Position of rover on map (1023, 1023).
bool env_map[map_dim][map_dim];     // Initialize map of type boolean.
std::vector<Point> Objects;
std::vector<Layer> Layers;
std::vector<Point> Steps;

struct activate_layers
{
  void operator()(Point &object)
  {
    for (int i = 0; i < Layers.size(); i++)
    {
      if (std::isgreaterequal(object.r, Layers[i].r)) // If object is in layer.
      {
        Layers[i].occupied = true; // Activate layer.
        break;                     // Stop searching through layers.
      }
    }
  }
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
  temp_point.x = temp_point.r * std::cos(theta);
  temp_point.y = temp_point.r * std::sin(theta);
  return temp_point;
}

void vectorize_scan(rplidar_response_measurement_node_hq_t nodes[8192], size_t count)
{
  for (int pos = 0; pos < (int)count; ++pos)
  {
    float angle = nodes[pos].angle_z_q14 * 90.f / (1 << 14); // Angle in degrees.
    float theta = (angle * 2 * 3.1416) / 360;                // Conversion to radians.
    float distance = nodes[pos].dist_mm_q2 / (1 << 2);       // Distance in mm.
    Objects.push_back(vectorize_point(theta, distance));     // Push to Object vector.
  }
}

int8_t calculate_speed()
{
  std::for_each(Objects.begin(), Objects.end(), activate_layers());
  const int n_layers = Layers.size();
  for (int i = 0; i < n_layers; i++)
  {
    if (Layers[i].occupied)
      return (int8_t)((255 / n_layers) * i);
  }
}

Circle buffer_forward(Circle buffer_circle, std::vector<Point> objects)
{
  while (!inside_circle(buffer_circle, objects))
  {
    buffer_circle.y += body_unit;
  }
  buffer_circle.y -= body_unit;
  return buffer_circle;
}

bool try_buffer_up(Circle buffer_circle)
{
  // Check if buffer circle can be moved up without conflict.
}

Circle advance_buffer(Circle buffer_circle, std::vector<Point> objects, Point goal)
{
  int dx = goal.x - buffer_circle.x;
  int dy = goal.y - buffer_circle.y;
  if (dx > body_unit && dy < -body_unit)
  {
    if (try_buffer_up(buffer_circle))
    {
      // Do something if buffer can be moved up.
    }
    else
    {
      // Move right since dx > 0.
    }
    
  }
}

std::queue<Point> navigator(Point goal, std::vector<Point> objects)
{
  // Return set of steps to assigned goal point.
  std::queue<Point> steps;      // Initialize queue.
  Circle buffer_circle;         // Initialize searcher-circle.
  buffer_circle.r = body_unit;  // Set buffer_circle radius.
  buffer_circle.x = base_point; // Set x-y position to rover position.
  buffer_circle.y = base_point;
  bool circle_clear = true;
  char last_flag = 'f';

  while (circle_clear)
  {
    circle_clear = !inside_circle(buffer_circle, objects);
    Point temp_point;
    temp_point.x = buffer_circle.x;
    temp_point.y = buffer_circle.y;
    steps.push(temp_point);
    // buffer_circle.y += body_unit;  // Increment buffer circle forwards.
  }
}

void navHelper()
{
  char last_flag = 'f';
}

int main()
{
}
