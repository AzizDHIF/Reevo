#ifndef HBACO_h
#define HBACO_h

#include "Common.h"
#include <stddef.h>


#define dimension 3
#define NBITEMS 100
#define NBITEMS_100 100
#define NBITEMS_300 300
#define NBITEMS_500 500

/*typedef struct {
int *items_nonpris;
  int nombr_nonpris;
  int nombr;float fitness;
	int explored;
	double* f;
	int* d;
}ind;
*/
typedef struct pop_st  /* a population */
{
    int size;
    int maxsize;
    ind **ind_array;
} pop;

typedef struct genetic_op /* a genetic operator (2 point mutations)*/
{
  int p1;
  int p2;
} mut;

double pow(double, double);
double sqrt(double);
ind* ind_copy(ind *i);
void* chk_malloc(size_t size);
pop* create_pop(int maxsize, int dim);
ind* create_ind(int dim);
void complete_free_pop(pop *pp);
int dominates(ind *p_ind_a, ind *p_ind_b);
double random_nb(double,double);
void mutate(ind *x,mut *m);

int max(int a, int b);

double heuristic(int index_item, double weights[dimension][NBITEMS], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS], double profit[NBITEMS] );
double heuristic_eval_100(int index_item, double weights[dimension][NBITEMS_100], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_100], double profit[NBITEMS_100] );
double heuristic_eval_300(int index_item, double weights[dimension][NBITEMS_300], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_300], double profit[NBITEMS_300] );
double heuristic_eval_500(int index_item, double weights[dimension][NBITEMS_500], double capacity[dimension], int nb_voisinage, int voisinage[NBITEMS_500], double profit[NBITEMS_500] );

#endif
