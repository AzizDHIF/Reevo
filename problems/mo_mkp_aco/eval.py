import subprocess
import sys
import os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


def remove_empty_line(path_file_txt):
    """
    Supprime les lignes vides d'un fichier texte.
    """
    with open(path_file_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(path_file_txt, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip():  # conserve uniquement les lignes non vides
                f.write(line)

def run_aco(executable="WeightACO_train", args=[]):
    run_cmd = [f"./{executable}.exe"] + args
    print(f"Exécution : {' '.join(run_cmd)}")
    
    result = subprocess.run(run_cmd, cwd=WORK_DIR)  
    
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




def concatenate_pareto_sets(pareto_dir, executable="nondominated"):

    result_file = os.path.join(pareto_dir, "final_pareto.txt")

    with open(result_file, "w") as out:
        for j in range(1, 11):
            pareto_file = os.path.join(pareto_dir, f"pareto_{j}.txt")

            with open(pareto_file, "r") as f:
                if j==10:
                 out.write(f.read())
                else:
                    out.write(f.read())
                    out.write("\n")
    
    remove_empty_line(result_file)


    run_cmd_filtrage = [
        f"./{executable}.exe",
        "--filter",
        result_file
    ]

    print("Exécution :", " ".join(run_cmd_filtrage))

    result_filtrage = subprocess.run(
        run_cmd_filtrage,
        cwd=WORK_DIR
    )

    if result_filtrage.returncode != 0:
        print(f"Erreur à l'exécution (code {result_filtrage.returncode})")
        sys.exit(1)

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

def calculate_meanHypervolume(files):
    
    mean=0

    for pareto_file in files:
        
        run_cmd_hv = [
            "./hv.exe",
            pareto_file,
            
            
        ]

        print("Exécution :", " ".join(run_cmd_hv))

        result_hv = subprocess.run(
            run_cmd_hv,
            cwd=WORK_DIR,
            capture_output=True,
            text=True)
        
        print(f"Résultat de l'hypervolume pour {pareto_file} : {result_hv.stdout}")
        try:
         mean=mean+float(result_hv.stdout)
        except ValueError:
            print(f"Erreur de conversion pour {pareto_file} : '{result_hv.stdout.strip()}' n'est pas un nombre valide.")
            raise ValueError(f"Erreur de conversion pour {pareto_file} : '{result_hv.stdout.strip()}' n'est pas un nombre valide.")
    mean=mean/len(files)
    print("moyenne pour l'hypervolume :", mean)
    return mean

def calculate_meanEpsilon(files):

    
    mean=0
    pareto_ref_list=[r"dataset\mood_train_dataset\dataset_0\pareto_ref.txt",r"dataset\mood_train_dataset\dataset_1\pareto_ref.txt",r"dataset\mood_train_dataset\dataset_2\pareto_ref.txt",r"dataset\mood_train_dataset\dataset_3\pareto_ref.txt",r"dataset\mood_train_dataset\dataset_4\pareto_ref.txt"]
    for pareto_ref, pareto_file in zip(pareto_ref_list, files):
        
        
        run_cmd_hv = [
            "./epsilon.exe",
            "--reference",
            pareto_ref,
            pareto_file
        ]

        print("Exécution :", " ".join(run_cmd_hv))

        result_ep = subprocess.run(
            run_cmd_hv,
            cwd=WORK_DIR,
            capture_output=True,
            text=True)
        
        print(f"Résultat de l'epsilon pour {pareto_file} : {result_ep.stdout}")
        try:
          mean=mean+float(result_ep.stdout)
        except ValueError:
            print(f"Erreur de conversion pour {pareto_file} : '{result_ep.stdout.strip()}' n'est pas un nombre valide.")
            raise ValueError(f"Erreur de conversion pour {pareto_file} : '{result_ep.stdout.strip()}' n'est pas un nombre valide.")
    mean=mean/len(files)
    print("moyenne pour l'epsilon :", mean)

    return mean 



if __name__ == "__main__":
    print("[*] Running ...")
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
    
    
    pareto_set_dirs=["pareto_set\\pareto_sets_dataset_0","pareto_set\\pareto_sets_dataset_1","pareto_set\\pareto_sets_dataset_2","pareto_set\\pareto_sets_dataset_3","pareto_set\\pareto_sets_dataset_4"]
    pareto_set_files=[os.path.join(p, "final_pareto.txt_dat") for p in pareto_set_dirs]
    pareto_ref_files=["dataset\\mood_train_dataset\\dataset_0\\reference_pareto.txt","dataset\\mood_train_dataset\\dataset_1\\reference_pareto.txt","dataset\\mood_train_dataset\\dataset_2\\reference_pareto.txt","dataset\\mood_train_dataset\\dataset_3\\reference_pareto.txt","dataset\\mood_train_dataset\\dataset_4\\reference_pareto.txt"]
    

    mood = sys.argv[3]
    print(f"[*] Mood: {mood}")
    assert mood in ["train", "val"]


    if mood == 'train':
        print("[*] Running ACO on training datasets...")
    
        #lancer l'ACO sur les datasets du train
        """for dataset in datasets:
            run_aco(args=[dataset])"""
        
        print("[*] Extracting Pareto sets from ACO results...")

        #extraire les sets de pareto à partir des résultats de l'ACO
        """for (algo_result_file, pareto_output_dir) in aco_results:
            extraire_pareto_sets(algo_result_file, pareto_output_dir)"""
        
        print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
        #concaténer les sets de pareto extraits pour chaque dataset

        """for pareto_dir in pareto_set_dirs:
            concatenate_pareto_sets(pareto_dir)"""
        
        

        print("[*] Calculating  hypervolume and epsilon...")
        #calcul des deux métriques epsilon et hypervolume
        
        
        ##hypervolume
        mean_hypervolume=calculate_meanHypervolume(pareto_set_files)
        ##epsilon
        mean_epsilon=calculate_meanEpsilon(pareto_set_files)

        print("[*] moyenne pour hypervolume et  epsilon:")
        print(mean_hypervolume, mean_epsilon)

    #mood = test:
    else:
        pass



  

