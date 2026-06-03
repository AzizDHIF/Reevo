import subprocess
import sys
import os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pareto_reference_set_calculation(dataset_path,executable="WeightACO_ref"):
    pass

def run_aco(executable="WeightACO_train", args=[]):
    run_cmd = [f"./{executable}.exe"] + args
    print(f"Exécution : {' '.join(run_cmd)}")
    
    result = subprocess.run(run_cmd, cwd=WORK_DIR)  # sans capture_output pour voir les erreurs
    
    if result.returncode != 0:
        print(f"Erreur à l'exécution (code {result.returncode})")
        sys.exit(1)

def extraire_pareto_sets(fichier_entree, dossier_sortie):
    import os

    os.makedirs(dossier_sortie, exist_ok=True)

    fichier_sortie = None
    compteur = 0

    with open(fichier_entree, 'r') as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue

            if ligne.startswith("mcycle"):
                if fichier_sortie:
                    fichier_sortie.close()
                compteur += 1
                chemin = os.path.join(dossier_sortie, f"pareto_{compteur}.txt")
                fichier_sortie = open(chemin, 'w')
                continue

            # Écrire uniquement les lignes de points (3 flottants)
            parties = ligne.split()
            if len(parties) == 3:
                try:
                    parties_negatives=[-1*float(x) for x in parties]
                    ligne_negative = "\t".join(str(v) for v in parties_negatives)

                    fichier_sortie.write(ligne_negative + "\n")
                except ValueError:
                    pass

    if fichier_sortie:
        fichier_sortie.close()

    print(f"{compteur} fichiers créés dans '{dossier_sortie}'")


def calculate_ref_point(pareto_path):

    points = []

    with open(pareto_path, "r") as f:
        for line in f:

            line = line.strip()

            if not line:
                continue

            values = [float(x) for x in line.split()]
            points.append(values)

    if not points:
        raise ValueError("No points found in file.")

    nb_obj = len(points[0])

    ref = []

    for j in range(nb_obj):

        column = [p[j] for p in points]

        minimum = min(column)
        maximum = max(column)

        ref_value = maximum + 0.1 * (maximum - minimum)

        ref.append(ref_value)

    return ",".join(f"{x:.6f}" for x in ref)



if __name__ == "__main__":
    datasets = [
        "dataset\\mood_train_dataset\\dataset_0_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_1_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_2_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_3_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_4_instance_100_items_3_objectifs.txt",
    ]
    aco_results=[("results_train_dataset_0.txt", "pareto_set\\pareto_sets_dataset_0"),
                 ("results_train_dataset_1.txt", "pareto_set\\pareto_sets_dataset_1"),
                 ("results_train_dataset_2.txt", "pareto_set\\pareto_sets_dataset_2"),
                 ("results_train_dataset_3.txt", "pareto_set\\pareto_sets_dataset_3"),
                 ("results_train_dataset_4.txt", "pareto_set\\pareto_sets_dataset_4")]
    

    """for (algo_result_file, pareto_output_dir) in aco_results:
        extraire_pareto_sets(algo_result_file, pareto_output_dir)
    compile_aco()
    for dataset in datasets:
        run_aco(args=[dataset])
    
    pareto_path="pareto_set\\pareto_sets_dataset_0\\pareto_1.txt"
    print(f"Calcul des points de référence : {calculate_ref_point(pareto_path)}")"""

    #Calcul de fronts de référence pour les 5 datasets:

    for i in range(5):
        pareto_path=f"pareto_set\\pareto_sets_dataset_{i}"
        run_pareto_reference_set_calculation(pareto_path)
        print(f"Dataset {i} : reference set calculated")
    