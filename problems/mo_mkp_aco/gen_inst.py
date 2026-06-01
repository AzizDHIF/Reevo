import os

import numpy as np

def gen_instance(n, m, m_objective):
    '''

    Generate *well-stated* MO-MKP instances
    Args:
        n: # of items
        m: # of constraints (problem dimensionality)
        m_objective: # number of objectives 
    
    '''
    prize = np.random.rand(n,m_objective)
    weight_matrix = np.random.rand(n, m)
   
    constraints = np.random.uniform(low=weight_matrix.max(0), high=weight_matrix.sum(0))
    # after norm, constraints are all 1
    weight_matrix = weight_matrix  / constraints.reshape(1, *constraints.shape)
    return prize, weight_matrix # (n, ), (n, m)

def save_instance(n, m, m_objective, prize, weight_matrix, constraints, filename):
    '''
    Save instance to a .txt file in the format expected by loadMOKP()
    Args:
        n: # of items
        m: # of constraints = # of objectives (nf=m=m_objective ici)
        m_objective: # of objectives
        prize: (n, m_objective) profit matrix
        weight_matrix: (n, m) weight matrix (already normalized)
        constraints: (m,) capacity vector
        filename: output file path
    '''
    with open(filename, 'w') as f:
        
        # ligne 1 : nf ni
        f.write(f"{m} {n}\n")

        # pour chaque contrainte/objectif
        for c in range(m):
            
            # capacité de la contrainte c
            # puisque weight_matrix est normalisé par constraints,
            # la capacité réelle est 1.0 après normalisation
            f.write(f"{1.0:.6f}\n")

            # pour chaque objet
            for i in range(n):
                f.write(f"item_{i}\n")
                f.write(f"{weight_matrix[i][c]:.6f}\n")
                f.write(f"{prize[i][c]:.6f}\n")
    f.close()

def generate_dataset(folder_path, n, m,m_objective, batch_size=64):
    prizes = []
    weights = []
    for batch_idx in range(batch_size):
        prize, weight = gen_instance(n, m, m_objective)
        file_path=os.path.join(folder_path, f"dataset_{batch_idx}_instance_{n}_items_{m}_objectifs.txt")
        save_instance(n, m, m_objective, prize, weight, np.ones(m), file_path)
   

def generate_datasets(basepath = None):
    import os
    basepath = basepath or os.path.join(os.path.dirname(__file__), "dataset")
    os.makedirs(basepath, exist_ok=True)

    
   
    for mood, seed, problem_sizes,list_m in [
        ('train', 1234, (100,),(3,)),
        ('val',   3456, (100, 300, 500),(3,)),
        ('test',  4567, (100, 250,  500, 750),(2,3,4)),
    ]:
        np.random.seed(seed)
        batch_size = 5 if mood == 'train' or mood == 'val' else 64
        for n in problem_sizes:
            for m in list_m:
                folderpath = os.path.join(basepath, f"mood_{mood}_dataset")
                os.makedirs(folderpath, exist_ok=True)
                generate_dataset(folderpath, n, m,m_objective=m, batch_size=batch_size)

if __name__=="__main__":
    generate_datasets()