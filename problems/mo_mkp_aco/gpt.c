#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS]) 
{
    double total_weight = 0.0;
    double remaining_capacity = 0.0;
    double total_profit = 0.0;
    int promising_item_count = 0;

    for (int j = 0; j < dimension; j++) {
        total_weight += weights[j][index_item];
        remaining_capacity += capacity[j] - weights[j][index_item];
    }

    double proximity = 0.0;
    for (int i = 0; i < nb_voisinage; i++) {
        int neighbour_index = voisinage[i];
        double neighbour_weight = 0.0;
        double neighbour_capacity_ratio = 0.0;

        for (int j = 0; j < dimension; j++) {
            neighbour_weight += weights[j][neighbour_index];
            neighbour_capacity_ratio += weights[j][neighbour_index] / capacity[j];
        }

        double neighbour_profit = profit[neighbour_index];
        double neighbour_value = neighbour_profit / neighbour_weight;

        if (neighbour_weight <= remaining_capacity && neighbour_capacity_ratio <= 1.0) {
            total_profit += neighbour_profit;
            promising_item_count++;
            proximity += 1.0 / neighbour_weight;
        }
    }

    double density = profit[index_item] / total_weight;
    double average_value = (promising_item_count > 0) ? total_profit / promising_item_count : 0.0;
    double capacity_ratio = total_weight / remaining_capacity;

    if (density > average_value && capacity_ratio < 1.0) {
        return density * (1 + average_value) * (1 + proximity);
    } else {
        return 0.0;
    }
}
