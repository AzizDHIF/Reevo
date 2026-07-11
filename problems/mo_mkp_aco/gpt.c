#include "HBACO.h"
double heuristic_eval_500(int index_item, double weights[dimension][NBITEMS_500], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_500], double profit[NBITEMS_500] ){
    int h=0;
    for(int j=0;j<dimension;j++){
			h=h+weights[j][voisinage[index_item]]/capacity[j]; 
			}
    return profit[voisinage[index_item]]/h;}