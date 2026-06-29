#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS] ){
    // Calculate the remaining capacity after selecting the current item
    double remaining_capacity[dimension];
    for (int j = 0; j < dimension; j++) {
        remaining_capacity[j] = capacity[j] - weights[j][index_item];
    }

    // Calculate the total capacity of all knapsacks in all dimensions
    double total_capacity = 0;
    for (int j = 0; j < dimension; j++) {
        total_capacity += capacity[j];
    }

    // Calculate the average weight and profit of neighboring items
    double avg_weight_neighbour[dimension] = {0};
    double avg_profit_neighbour = 0;
    for (int i = 0; i < nb_voisinage; i++) {
        for (int j = 0; j < dimension; j++) {
            avg_weight_neighbour[j] += weights[j][voisinage[i]] / nb_voisinage;
        }
        avg_profit_neighbour += profit[voisinage[i]] / nb_voisinage;
    }

    // Calculate the weight-to-profit ratio of the current item and its neighbors
    double item_ratio = profit[index_item] / (total_capacity - remaining_capacity[0]); // simplified to one dimension for demonstration
    double neighbour_ratio = avg_profit_neighbour / (total_capacity - remaining_capacity[0]); // simplified to one dimension for demonstration

    // Combine various factors using linear combination
    double score = 0.5 * item_ratio + 0.3 * neighbour_ratio;

    // Sparsify the heuristic by setting unpromising elements to zero
    if (score < 0.1 || remaining_capacity[0] < 0) {
        score = 0;
    }

    return score;
}
