#include <algorithm>
#include <stdlib.h>
#include <cstdio>
#include <omp.h>
#include <vector>
#include "func.h"

const int THRESHOLD = 1000;

void sequentialMergeSort(std::vector<int> &arr, int left, int right)
{
  if (left >= right)
    return;

  int mid = (right + left) / 2;
  sequentialMergeSort(arr, left, mid);
  sequentialMergeSort(arr, mid + 1, right);
  std::inplace_merge(arr.begin() + left, arr.begin() + mid + 1, arr.begin() + right + 1);
}

void mergeSort(std::vector<int> &arr, int left, int right)
{
  if (left >= right)
    return;

  if ((right - left) < THRESHOLD)
  {
    sequentialMergeSort(arr, left, right);
    return;
  }

  int mid = left + (right - left) / 2;
#pragma omp task shared(arr)
  mergeSort(arr, left, mid);
#pragma omp task shared(arr)
  mergeSort(arr, mid + 1, right);
#pragma omp taskwait
  std::inplace_merge(arr.begin() + left, arr.begin() + mid + 1, arr.begin() + right + 1);
}

void printVector(std::vector<int> &arr)
{
  for (int val : arr)
    std::printf(" %d ", val);
}
