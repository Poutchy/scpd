#include <algorithm>
#include <cstdio>
#include <vector>
#include "func.h"


void mergeSort(std::vector<int>& arr, int left, int right)
{
  if (left >= right)
    return;

  int mid = (right + left) / 2;
  mergeSort(arr, left, mid);
  mergeSort(arr, mid + 1, right);
  std::inplace_merge(arr.begin() + left, arr.begin() + mid + 1, arr.begin() + right + 1);
}

void printVector(std::vector<int>& arr)
{
  for (int val : arr)
    std::printf(" %d ", val);
}

