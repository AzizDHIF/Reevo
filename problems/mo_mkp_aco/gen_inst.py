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

def generate_dataset(filepath, n, m,m_objective, batch_size=64):
    prizes = []
    weights = []
    for _ in range(batch_size):
        prize, weight = gen_instance(n, m, m_objective)
        prizes.append(prize)
        weights.append(weight)
    prizes = np.stack(prizes)
    weights = np.stack(weights)
    np.savez(filepath, prizes = prizes, weights = weights)

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
                filepath = os.path.join(basepath, f"{mood}{n}_{m}_objectifs_dataset.npz")
                generate_dataset(filepath, n, m,m_objective=m, batch_size=batch_size)

if __name__ == '__main__':
    generate_datasets()

    