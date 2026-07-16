#include "HBACO.h"
double heuristic_eval_100(int index_item, double weights[dimension][NBITEMS_100], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_100], double profit[NBITEMS_100] ){
double h=0;
for(int j=0;j<dimension;j++){
h=h+weights[j][voisinage[index_item]]/capacity[j];
}
return profit[voisinage[index_item]]/h;}
