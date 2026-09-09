#include "HBACO.h"
double heuristic_eval_300(int index_item, double weights[dimension][NBITEMS_300], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_300], double profit[NBITEMS_300])
{
    double h = 0.001; // Initialize with a small value to avoid division by zero
    for (int j = 0; j < dimension; j++) {
        h += weights[j][voisinage[index_item]] / (capacity[j] + 0.001); // Adding a small value to capacity to avoid division by zero
    }
    return profit[voisinage[index_item]] / h;
}
