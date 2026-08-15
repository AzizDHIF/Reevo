#include "HBACO.h"
double heuristic_eval_300(int index_item, double weights[dimension][NBITEMS_300], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_300], double profit[NBITEMS_300]) {
    // Calculate the density of the item
    double density = 0;
    for (int j = 0; j < dimension; j++) {
        density += weights[j][index_item] / capacity[j];
    }

    // Calculate the remaining capacity after including the item
    double remaining_capacity = 1;
    for (int j = 0; j < dimension; j++) {
        remaining_capacity *= (capacity[j] - weights[j][index_item]) / capacity[j];
    }

    // Calculate the average profit of the neighborhood
    double sum_profit_voisinage = 0;
    double count_voisinage = 0;
    for (int i = 0; i < nb_voisinage; i++) {
        if (index_item != voisinage[i]) {
            sum_profit_voisinage += profit[voisinage[i]];
            count_voisinage++;
        }
    }
    double average_profit_voisinage = (count_voisinage > 0) ? sum_profit_voisinage / count_voisinage : 0;

    // Calculate the heuristic_eval_300 value
    double h = profit[index_item] / (density + 1e-6);
    h *= (1 + (average_profit_voisinage / (profit[index_item] + 1e-6)));
    h *= (remaining_capacity + 1e-6);

    // Sparsify the heuristic_eval_300
    if (h < 0.01) {
        return 0;
    }

    return h;
}
