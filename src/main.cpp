#include <chrono>
#include <cstdio>
#include <random>
#include <stdlib.h>
#include <vector>
#include "func.h"


#define BASE_VECTOR_SIZE 10

int main(int argc, char *argv[])
{
  int vector_size = BASE_VECTOR_SIZE;

  if (argc == 2)
    vector_size = std::stoi(argv[1]);

  std::vector<int> arr(vector_size);
  int rd = 42;
  std::mt19937 gen(rd);

  // random_device rd;
  // mt19937 gen(rd());

  std::uniform_int_distribution<> dis(0, 10000);

  for (int i = 0; i < vector_size; ++i)
    arr[i] = dis(gen);
  int n = vector_size;

  // start of the algorithm
  auto start = std::chrono::high_resolution_clock::now();

  mergeSort(arr, 0, n - 1);

  auto end = std::chrono::high_resolution_clock::now();
  
  std::chrono::duration<double> diff = end - start;

	for (int i=0; i<vector_size - 1; i++) {
		if (arr[i] > arr[i+1]) {
			std::fprintf(stderr, "Test FAILED: arr[%d] > arr[%d], expected %d < %d\n", i, i+1, arr[i], arr[i+1]);
		}
	}

  std::printf("Time: %f\n", diff.count());
  return 0;
}
