#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS]) {
    double total_capacity = 0.0;
    double weight_sum = 0.0;

    // Calculate total capacity and weight sum
    for (int j = 0; j < dimension; j++) {
        total_capacity += capacity[j];
        weight_sum += weights[j][index_item];
    }

    // Calculate item density
    double density = weight_sum / total_capacity;

    // Calculate neighborhood profit density
    double neighborhood_profit = 0.0;
    double neighborhood_weight = 0.0;
    for (int i = 0; i < nb_voisinage; i++) {
        neighborhood_profit += profit[voisinage[i]];
        for (int j = 0; j < dimension; j++) {
            neighborhood_weight += weights[j][voisinage[i]];
        }
    }

    // Calculate utilization
    double utilization = weight_sum / total_capacity;

    // Simplify calculations
    if (weight_sum == 0.0) {
        return profit[index_item];
    }

    // Calculate heuristic value
    double neighborhood_profit_density = (neighborhood_weight > 0) ? neighborhood_profit / neighborhood_weight : 0;
    double heuristic_value = (profit[index_item] / weight_sum) * utilization * (1 - density) * neighborhood_profit_density;

    // Prioritize item density and sparsify the heuristic
    if (heuristic_value < 0.01 || neighborhood_profit_density < 0.1 || density > 1) {
        heuristic_value = 0.0;
    }

    return heuristic_value;
}
