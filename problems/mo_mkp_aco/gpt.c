#include "HBACO.h"
double heuristic_eval_500(int index_item, double weights[dimension][NBITEMS_500], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_500], double profit[NBITEMS_500] ){
    double h = 0;
    double density = 0;
    double avg_weight = 0;
    double util = 0;

    // Calculate the average weight of the item across all dimensions
    for(int j = 0; j < dimension; j++){
        avg_weight += weights[j][index_item];
    }
    avg_weight /= dimension;

    // Calculate the density of the item based on its profit and average weight
    density = profit[index_item] / avg_weight;

    // Calculate the utilization factor of the item
    for(int j = 0; j < dimension; j++){
        util += (1 - (weights[j][index_item] / capacity[j]));
    }
    util /= dimension;

    // Sparsify the heuristic_eval_500 by setting unpromising elements to zero
    if (util < 0 || density < 0) {
        return 0;
    }

    // Combine various factors to determine how promising it is to select an item
    h = (profit[index_item] * util) / (avg_weight * (1 + nb_voisinage));

    return h;
}
