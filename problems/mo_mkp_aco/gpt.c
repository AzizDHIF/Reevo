#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS]) {
    // Calculate the weight and profit of the item
    double item_weight = 0;
    for (int j = 0; j < dimension; j++) {
        item_weight += weights[j][index_item];
    }
    double item_profit = profit[index_item];

    // Calculate the dimension-specific weights and profits of the item
    double dimension_weights[dimension];
    double dimension_profits[dimension];
    for (int j = 0; j < dimension; j++) {
        dimension_weights[j] = weights[j][index_item];
        dimension_profits[j] = item_profit * dimension_weights[j] / item_weight;
    }

    // Calculate the average weight and profit of the item's neighbors
    double avg_weights[dimension];
    double avg_profits[dimension];
    for (int j = 0; j < dimension; j++) {
        avg_weights[j] = 0;
        avg_profits[j] = 0;
    }
    int count = 0;
    for (int i = 0; i < nb_voisinage; i++) {
        double neighbor_weight = 0;
        for (int j = 0; j < dimension; j++) {
            neighbor_weight += weights[j][voisinage[i]];
            avg_weights[j] += weights[j][voisinage[i]];
            avg_profits[j] += profit[voisinage[i]] * weights[j][voisinage[i]] / neighbor_weight;
        }
        count++;
    }
    if (count > 0) {
        for (int j = 0; j < dimension; j++) {
            avg_weights[j] /= count;
            avg_profits[j] /= count;
        }

        // Calculate the dimension-specific scores of the item and its neighbors
        double item_scores[dimension];
        double neighbor_scores[dimension];
        for (int j = 0; j < dimension; j++) {
            item_scores[j] = dimension_profits[j] / dimension_weights[j];
            neighbor_scores[j] = avg_profits[j] / avg_weights[j];
        }

        // Use a weighted sum to combine the dimension-specific scores
        double combined_score = 0;
        for (int j = 0; j < dimension; j++) {
            combined_score += 0.4 * item_scores[j] + 0.3 * neighbor_scores[j] + 0.3 * (1 - dimension_weights[j] / capacity[j]);
        }
        combined_score /= dimension;

        // Sparsify the heuristic_eval_500 by setting unpromising elements to zero
        if (combined_score < 1e-6) {
            return 0;
        }

        return combined_score;
    } else {
        // If there are no neighbors, use only the item's score
        double item_score = item_profit / item_weight;
        return item_score;
    }
}
