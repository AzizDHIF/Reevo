#include "HBACO.h"
double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS]) {
    double h = 0;
    double total_weight = 0;
    double over_capacity = 0;
    int i, j;
    
    // Calculate total weight and check over-capacity
    for(j=0; j<dimension; j++){
        total_weight += weights[j][index_item] / capacity[j];
        if(weights[j][index_item] > capacity[j]){
            over_capacity = 1;
        }
    }
    
    // Penalize if over capacity
    if(over_capacity){
        return 0;  // Sparsify by setting to zero if violates capacity
    }
    
    // Compute average weight per dimension and neighbor's profit
    double avg_weight = total_weight / dimension;
    double neighbor_profit = 0;
    if(nb_voisinage > 0){
        for(i=0; i<nb_voisinage; i++){
            neighbor_profit += profit[voisinage[i]];
        }
        neighbor_profit /= nb_voisinage;
    }
    
    // Combine factors with different weights
    h = (profit[index_item] * 0.6) + (neighbor_profit * 0.2) + (1.0/avg_weight * 0.2);
    
    return h;
}
