#include <iostream>
#include <cmath>
#include <queue>

using namespace std;

const int map_dim = 2048;  // Size of map in each dimension.
int base_point = (map_dim / 2) - 1;  // Position of rover on map (1023, 1023). 
bool env_map[map_dim][map_dim];  // Initialize map of type boolean.

int scale_raw_distance(float distance) {
  // Scale distance readings so that results can be mapped on fixed size grid. 
  // Scales input from distance: [0, 5000] to result: [0, base_point]
  int max_distance = 5000;  // Distance reading should never exceed 5000 mm.
  int result = (distance * base_point) / max_distance;
  return result;
}

void plot_point(float theta, float distance) {  
  distance = scale_raw_distance(distance);
  int x_point = distance * cos(theta);
  int y_point = distance * sin(theta);
  // cout << '(' << x_point << ',' << y_point << ')' << '\n';
  if (abs(x_point) < base_point && abs(y_point) < base_point) {
    env_map[base_point + y_point][base_point + x_point] = '*';
  }
}

void plot_scan(rplidar_response_measurement_node_hq_t nodes[8192], size_t count) {
  for (int pos = 0; pos < (int)count; ++pos)
  {
		float angle = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
		float distance = nodes[pos].dist_mm_q2 / (1 << 2);
    plot_point(angle, distance);
  }
}

bool inside_circle(int[3] circle, int[2] object) {
  
}

void navigator() {
  // Return set of steps to assigned goal point.
  queue<int[2]> steps;


  
}

int main() {
  cout << "Size of bool: " << sizeof(bool);
}

