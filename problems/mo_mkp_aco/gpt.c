#include <math.h>
#include "HBACO.h"
double heuristic_eval_500(int index_item, double weights[dimension][NBITEMS_500], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_500], double profit[NBITEMS_500]) {
    double total_weight = 0.0;
    double total_profit = 0.0;

    // calculate the total weight and profit of the item and its neighbors
    for (int i = 0; i < nb_voisinage; i++) {
        for (int j = 0; j < dimension; j++) {
            total_weight += weights[j][voisinage[i]];
        }
        total_profit += profit[voisinage[i]];
    }

    // add the weight and profit of the current item
    for (int j = 0; j < dimension; j++) {
        total_weight += weights[j][index_item];
    }
    total_profit += profit[index_item];

    // calculate the heuristic_eval_500 value based on density (profit/weight) and capacity constraints
    if (total_weight > 0.0) {
        double density = total_profit / total_weight;
        double capacity_ratio = 1.0;
        for (int j = 0; j < dimension; j++) {
            capacity_ratio = capacity_ratio * (1.0 - (total_weight / capacity[j]));
        }
        capacity_ratio = pow(capacity_ratio, 1.0 / dimension);
        return density * capacity_ratio;
    } else {
        return 0.0;
    }
}
