#include <chrono>
#include <cstdio>
#include <algorithm>
#include <vector>
#include <random>
#include <mpi.h>
#include "func.h"

#define BASE_VECTOR_SIZE 10

int main(int argc, char *argv[])
{
  int vector_size = BASE_VECTOR_SIZE;   // default if no argument

  int myrank;
  int size;

  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &myrank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  if (argc == 2)
    vector_size = std::stoi(argv[1]);

  std::vector<int> arr;

  if (!myrank) {
    arr.resize(vector_size);
    int seed_random = 42;
    std::mt19937 gen(seed_random);

    // random_device rd;
    // mt19937 gen(rd());

    std::uniform_int_distribution<> distribution(0, 10000);

    for (int i = 0; i < vector_size; ++i)
      arr[i] = distribution(gen);
  }

  std::vector<int> counts(size);
  std::vector<int> displs(size);
  for (int i = 0; i < size; ++i) {
    auto start = vector_size * i / size;
    auto end = vector_size * (i + 1) / size;
    counts[i] = end - start;
    displs[i] = start;
  }

  int local_vector_size = counts[myrank];
  std::vector<int> local_arr(local_vector_size);

  std::chrono::high_resolution_clock::time_point start;
  if (!myrank)
    start = std::chrono::high_resolution_clock::now();

  MPI_Scatterv(
    arr.data(),
    counts.data(),
    displs.data(),
    MPI_INT,
    local_arr.data(),
    local_vector_size,
    MPI_INT,
    0,
    MPI_COMM_WORLD
  );

  mergeSort(local_arr, 0, local_vector_size - 1);

  MPI_Gatherv(
    local_arr.data(),
    local_vector_size,
    MPI_INT,
    arr.data(),
    counts.data(),
    displs.data(),
    MPI_INT,
    0,
    MPI_COMM_WORLD
  );
  if (!myrank) {
    // std::printf("\nPartially sorted vector:\n");
    // printVector(arr);
    // Merge all sorted chunks in-place into a single sorted array
    for (int i = 1; i < size; ++i) {
      int begin = 0;
      int mid = displs[i];
      int end = displs[i] + counts[i];

      std::inplace_merge(arr.begin() + begin, arr.begin() + mid, arr.begin() + end);
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> time = end - start;

    // std::printf("\nFully sorted vector:\n");
    // printVector(arr);

		for (int i=0; i<vector_size - 1; i++) {
			if (arr[i] > arr[i+1]) {
				std::fprintf(stderr, "Test FAILED: arr[%d] > arr[%d], expected %d < %d\n", i, i+1, arr[i], arr[i+1]);
				MPI_Abort(MPI_COMM_WORLD, 0);
			}
		}
    std::printf("Time: %f\n", time.count());
	}

  MPI_Finalize();
  return 0;
}

