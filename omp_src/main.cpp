#include <chrono>
#include <cstdio>
#include <omp.h>
#include <random>
#include <stdlib.h>
#include "func.h"

// #define BASE_VECTOR_SIZE 10
// #ifndef OMP_NUM_THREADS
// #define OMP_NUM_THREADS 10
// #endif

int main(int argc, char *argv[])
{
  long vector_size;
  long nth;

  if (argc >= 2)
  {
    vector_size = std::stol(argv[1]);
  }
  else
  {
    vector_size = 20;
  }
  if (argc == 3)
  {
    nth = std::stoi(argv[2]);
  }
  else
  {
    nth = 10;
  }

  std::printf("nth: %ld\n", nth);
  std::printf("vector_size: %ld\n", vector_size);

  std::vector<int> arr(vector_size);
  int rd = 42;
  std::mt19937 gen(rd);

  // random_device rd;
  // mt19937 gen(rd());

  std::uniform_int_distribution<> dis(0, 10000);

  for (int i = 0; i < vector_size; ++i)
    arr[i] = dis(gen);

  // cout << "Given vector is \n";
  // printVector(arr);
  auto start = std::chrono::high_resolution_clock::now();

#pragma omp parallel num_threads(nth)
  {
#pragma omp single
    mergeSort(arr, 0, vector_size - 1);
  }
  // std::printf("\nSorted vector is \n");
  // printVector(arr);
  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> time = end - start;

  for (int i = 0; i < vector_size - 1; i++)
  {
    if (arr[i] > arr[i + 1])
    {
      std::fprintf(stderr, "Test FAILED: arr[%d] > arr[%d], expected %d < %d\n", i, i + 1, arr[i], arr[i + 1]);
    }
  }

  std::printf("Time: %f\n", time.count());

  return 0;
}
