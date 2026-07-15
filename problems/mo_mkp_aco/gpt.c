#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS]) 
{
    double max_weight = 0;
    double min_weight = 1e10;
    double avg_weight = 0;
    double total_capacity = 0;
    double utilization_ratio = 0;
    double score = 0;
    double profit_per_weight = 0;
    double capacity_ratio = 0;

    // Calculate average weight and total capacity
    for(int j = 0; j < dimension; j++) {
        double w = weights[j][index_item];
        max_weight = (w > max_weight) ? w : max_weight;
        min_weight = (w < min_weight) ? w : min_weight;
        avg_weight += w;
        total_capacity += capacity[j];
    }

    // Simplify calculations
    avg_weight /= dimension;
    utilization_ratio = avg_weight / (total_capacity / dimension);

    // Prioritize profitability and minimize dependencies
    profit_per_weight = profit[index_item] / avg_weight;

    // Consider the neighborhood of the item
    double neighborhood_profit = 0;
    for(int i = 0; i < nb_voisinage; i++) {
        neighborhood_profit += profit[voisinage[i]];
    }
    neighborhood_profit /= nb_voisinage;

    // Evaluate items multidimensionally
    capacity_ratio = min_weight / max_weight;
    double weight_variance = 0;
    for(int j = 0; j < dimension; j++) {
        weight_variance += (weights[j][index_item] - avg_weight) * (weights[j][index_item] - avg_weight);
    }
    weight_variance /= dimension;

    // Combine various factors to determine the heuristic score
    score = profit_per_weight * (1 - utilization_ratio) * capacity_ratio * (1 - (weight_variance / (avg_weight * avg_weight)));

    // Consider the overall profit and neighborhood profit
    score *= (1 + neighborhood_profit / profit[index_item]);

    // Sparsify the heuristic by setting unpromising elements to zero
    if(score < 0) score = 0;

    return score;
}
