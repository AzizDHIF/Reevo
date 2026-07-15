import subprocess
import sys
import os
import logging
from pathlib import Path
RUN_DIR = Path(os.getcwd())  # dossier créé par Hydra pour cette exécution
WORK_DIR = os.path.dirname(os.path.abspath(__file__))


import re

possible_func_names = ["heuristic", "heuristic_v1", "heuristic_v2", "heuristic_v3"]
population_size=4

def print_hyperlink(path, text=None):
    """Print hyperlink to file or folder for convenient navigation"""
    # Format: \033]8;;file:///path/to/file\033\\text\033]8;;\033\\
    text = text or path
    full_path = f"file://{os.path.abspath(path)}"
    return f"\033]8;;{full_path}\033\\{text}\033]8;;\033\\"

def write_heuristic_train(input_txt_path: str, output_c_path: str) -> None:
   
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Construit un pattern qui matche n'importe quel nom de la liste
    pattern = r'\b(' + '|'.join(re.escape(name) for name in possible_func_names) + r')\b'

    new_content, count = re.subn(pattern, 'heuristic', content)

    if count == 0:
        raise ValueError(
            f"Aucun nom de fonction parmi {possible_func_names} trouvé dans '{input_txt_path}'"
        )

    with open(output_c_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def write_heuristic_eval(input_txt_path: str, output_c_path: str,nbitems: str) -> None:
   
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Construit un pattern qui matche n'importe quel nom de la liste
    pattern = r'\b(' + '|'.join(re.escape(name) for name in possible_func_names) + r')\b'
    pattern_2= 'NBITEMS'
    new_content, count = re.subn(pattern, f'heuristic_eval_{nbitems}', content)

    if count == 0:
        raise ValueError(
            f"Aucun nom de fonction parmi {possible_func_names} trouvé dans '{input_txt_path}'"
        )
        
    new_content,count=re.subn(pattern_2,f'NBITEMS_{nbitems}',new_content)
    with open(output_c_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def compile(c_file_name,exe_file_name):
    run_cmd = ["gcc", c_file_name, "gpt.c", "-o", exe_file_name]

    result=subprocess.run(run_cmd,cwd=WORK_DIR)

    if result.returncode!=0:
        raise("Erreur de compilation")
    
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

def run_aco(executable, args=[]):
    exe_path = os.path.join(WORK_DIR, f"{executable}.exe")  # défini EN PREMIER
    run_cmd = [exe_path] + args  # chemin absolu directement dans la commande
    
    try:
        result = subprocess.run(run_cmd, cwd=WORK_DIR)
    except FileNotFoundError as e:
        print(f"[ERREUR] FileNotFoundError : {e}")
        raise

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




def concatenate_pareto_sets(pareto_dir,nb_pareto_files, executable=os.path.join(WORK_DIR,"nondominated")):

    result_file = os.path.join(pareto_dir, "final_pareto.txt")

    with open(result_file, "w") as out:
        for j in range(1, nb_pareto_files+1):
            pareto_file = os.path.join(pareto_dir, f"pareto_{j}.txt")

            with open(pareto_file, "r") as f:
                if j==10:
                 out.write(f.read())
                else:
                    out.write(f.read())
                    out.write("\n")
    
    remove_empty_line(result_file)


    run_cmd_filtrage = [
        f"{executable}.exe",
        
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




def get_profits_range(dataset_path):
    
    
    
    with open(dataset_path, "r") as f:
        l=f.readline().strip().split()
        n_dim=int(l[0])
        n_items=int(l[1])
        
    
        max_profits = n_dim*[""]
        min_profits = n_dim*[""]
        etendu_profits=n_dim*[""]

        for index_dim in range(n_dim):

            f.readline() #skip the capacity line
            profits=[]
            for item in range(n_items):
                    
                f.readline() #skip line with item index
                f.readline() #skip weight
                profits.append(float(f.readline().strip()))
            max_profits[index_dim]=max(profits)
            min_profits[index_dim]=min(profits)
            etendu_profits[index_dim]=max(profits) -min(profits)
    
    return max_profits,min_profits,etendu_profits


            


def calculate_meanHypervolume(files):
    
    mean=0
    

    for pareto_file in files:
        if fichier_vide_ou_une_ligne(pareto_file):
            continue 
        
        print("Exécution :", " ".join([os.path.join(WORK_DIR,"hv.exe"), pareto_file,]))

        result_hv = subprocess.run(
            [os.path.join(WORK_DIR,"hv.exe"), pareto_file],
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

def calculate_meanEpsilon(files, pareto_ref_files):

    
    mean=0
  
    for pareto_file, pareto_ref  in zip(files,pareto_ref_files):
        
        
        run_cmd_ep = [
            os.path.join(WORK_DIR,"epsilon.exe"),
            "--reference",
            pareto_ref,
            pareto_file
        ]

        print("Exécution :", " ".join(run_cmd_ep))

        result_ep = subprocess.run(
            run_cmd_ep,
            cwd=WORK_DIR,
            capture_output=True,
            text=True)
        
        print(f"Résultat de l'epsilon pour {pareto_file} : {result_ep.stdout}")
        try:
          
          epsilon = float(result_ep.stdout.strip())
          mean=mean+epsilon
        except ValueError:
            print(f"returncode: {result_ep.returncode}")
            print(f"stdout: '{result_ep.stdout}'")
            print(f"stderr: '{result_ep.stderr}'")
            print(f"Erreur de conversion pour {pareto_file} : '{result_ep.stdout.strip()}' n'est pas un nombre valide.")
            raise ValueError(f"Erreur de conversion pour {pareto_file} : '{result_ep.stdout.strip()}' n'est pas un nombre valide.")
    
    mean=mean/len(files)
    print("moyenne pour l'epsilon :", mean)

    return mean 


def delete_folder(folder_path):
    cmd = [
        "powershell",
        "-Command",
        f"Remove-Item -Path '{folder_path}' -Recurse -Force"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Erreur lors de la suppression : {result.stderr}"
        )

def delete_file(file_path):
    cmd = [
        "powershell",
        "-Command",
        f"Remove-Item -Path '{file_path}' -Force"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Erreur lors de la suppression : {result.stderr}"
        )
   

def get_pareto_ref_etendue(pareto_ref_path):
    points = []
    with open(pareto_ref_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                points.append([float(x) for x in line.split()])
    
    nb_obj = len(points[0])
    etendues = [
        max(p[j] for p in points) - min(p[j] for p in points)
        for j in range(nb_obj)
    ]
    return sum(etendues) / len(etendues)


def fichier_vide_ou_une_ligne(chemin_fichier):
    """
    Retourne True si le fichier ne contient aucune ligne ou une seule ligne,
    False sinon.
    """
    with open(chemin_fichier, 'r') as f:
        lignes = [ligne for ligne in f if ligne.strip()]  # ignore les lignes vides
    return len(lignes) <= 1


import shutil

def copy_folder_to_run_dir(source_dir: str, dest_dir: Path, folder_name: str = None) -> Path:
    """Copie un dossier local (et son contenu) vers le dossier de l'exécution en cours."""
    source_dir = Path(source_dir)
    if folder_name is None:
        folder_name = source_dir.name
    dest_path = dest_dir / folder_name

    shutil.copytree(source_dir, dest_path, dirs_exist_ok=True)
    logging.info(f"Dossier copié: {print_hyperlink(dest_path)}")
    return dest_path


if __name__ == "__main__":
    print("[*] Running ...")
    mood = sys.argv[2]

    datasets = [
        "dataset\\mood_train_dataset\\dataset_0_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_1_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_2_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_3_instance_100_items_3_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_4_instance_100_items_3_objectifs.txt",
    ]
    
    
    print(f"[*] Mood: {mood}")
    assert mood in ["train", "val"]


    if mood == 'train':
        id_response=f"results_individual_{sys.argv[1]}"

        aco_results=[(os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_0.txt"), os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_0")),
                 (os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_1.txt"), os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_1")),
                 (os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_2.txt"), os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_2")),
                 (os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_3.txt"), os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_3")),
                 (os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_4.txt"), os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_4"))]
    
        result_files=[f"{id_response}\\results_train_dataset_{i}.txt" for i in range(5)]
        pareto_set_dirs=[l[1] for l in aco_results]
        pareto_set_files=[os.path.join(p, "final_pareto.txt_dat") for p in pareto_set_dirs]
        pareto_ref_files=[os.path.join(WORK_DIR,r"dataset\mood_train_dataset\ref_dataset_0\final_pareto_file.txt_dat"),os.path.join(WORK_DIR,r"dataset\mood_train_dataset\ref_dataset_1\final_pareto_file.txt_dat"),os.path.join(WORK_DIR,r"dataset\mood_train_dataset\ref_dataset_2\final_pareto_file.txt_dat"),os.path.join(WORK_DIR,r"dataset\mood_train_dataset\ref_dataset_3\final_pareto_file.txt_dat"),os.path.join(WORK_DIR,r"dataset\mood_train_dataset\ref_dataset_4\final_pareto_file.txt_dat")]

        os.makedirs(os.path.join(WORK_DIR,id_response), exist_ok=True)

        print("[*] compiling ... ")
        
        write_heuristic_train(os.path.join(WORK_DIR,"gpt.txt"),os.path.join(WORK_DIR,"gpt.c"))

        compile("WeightACO_train_100items.c",f"WeightACO_train_100items_{id_response}.exe")

        #lancer l'ACO sur les datasets du train
        print("[*] Running ACO on training datasets...")

        for dataset,res_file in zip(datasets,result_files):
            run_aco(f"WeightACO_train_100items_{id_response}",args=[dataset, res_file])

        print("[*] Extracting Pareto sets from ACO results...")

        #extraire les sets de pareto à partir des résultats de l'ACO
        for (algo_result_file, pareto_output_dir) in aco_results:
            extraire_pareto_sets(algo_result_file, pareto_output_dir)
        
        print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
        #concaténer les sets de pareto extraits pour chaque dataset

        for pareto_dir in pareto_set_dirs:
            concatenate_pareto_sets(pareto_dir,3)
        
        print("[*] Calculating  hypervolume and epsilon...")
        #calcul des deux métriques epsilon et hypervolume
        
        ##hypervolume
        mean_hypervolume=calculate_meanHypervolume(pareto_set_files)
        ##epsilon
        mean_epsilon=calculate_meanEpsilon(pareto_set_files,pareto_ref_files)
        
        #Supprimer les dossiers de sets de pareto temporaire
        print("[*] Suppression des dossiers de sets de pareto intermédiaires...")
        for i in range(5):
            delete_folder(os.path.join(WORK_DIR,f"{id_response}\\pareto_set\\pareto_sets_dataset_{i}"))
            #Supprimer les fichiers de résultats intermédiaires de l'ACO
            delete_file(os.path.join(WORK_DIR,f"{id_response}\\results_train_dataset_{i}.txt"))

        print("[*] moyenne pour hypervolume :")
        
        print(mean_hypervolume)

        


   
    #mood = val:
    else:
        logging.info(f"[*] Evaluating ...")
        os.makedirs(os.path.join(WORK_DIR,"pareto_set_val"), exist_ok=True)
        from itertools import product
        val_aco_results=[(os.path.join(WORK_DIR,"results_val_dataset_0_100_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_0_items_100")),
                 (os.path.join(WORK_DIR,"results_val_dataset_1_100_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_1_items_100")),
                 (os.path.join(WORK_DIR,"results_val_dataset_2_100_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_2_items_100")),
                 (os.path.join(WORK_DIR,"results_val_dataset_3_100_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_3_items_100")),
                 (os.path.join(WORK_DIR,"results_val_dataset_4_100_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_4_items_100")),
                 (os.path.join(WORK_DIR,"results_val_dataset_0_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_0_items_300")),
                 (os.path.join(WORK_DIR,"results_val_dataset_1_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_1_items_300")),
                 (os.path.join(WORK_DIR,"results_val_dataset_2_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_2_items_300")),
                 (os.path.join(WORK_DIR,"results_val_dataset_3_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_3_items_300")),
                 (os.path.join(WORK_DIR,"results_val_dataset_4_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_4_items_300")),
                 (os.path.join(WORK_DIR,"results_val_dataset_0_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_0_items_500")),
                 (os.path.join(WORK_DIR,"results_val_dataset_1_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_1_items_500")),
                 (os.path.join(WORK_DIR,"results_val_dataset_2_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_2_items_500")),
                 (os.path.join(WORK_DIR,"results_val_dataset_3_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_3_items_500")),
                 (os.path.join(WORK_DIR,"results_val_dataset_4_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_4_items_500")),]
        
        
        val_pareto_ref_files_100items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_100_items\\final_pareto_file.txt_dat") for i in range(5)]
        val_pareto_ref_files_300items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_300_items\\final_pareto_file.txt_dat") for i in range(5)]
        val_pareto_ref_files_500items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_500_items\\final_pareto_file.txt_dat") for i in range(5)]
        val_pareto_set_files=[os.path.join(p, "final_pareto.txt_dat") for _,p in val_aco_results]
        val_pareto_set_files_100items=[f for f  in  val_pareto_set_files if "items_100" in f] 
        val_pareto_set_files_300items=[f for f  in  val_pareto_set_files if "items_300" in f]
        val_pareto_set_files_500items=[f for f  in  val_pareto_set_files if "items_500" in f]
        
       
        print("[*] Running ACO on EVAL datasets...")

        #lancer l'ACO sur les datasets du train


                   
        for nb_items in [100,300,500]:
            
            print("[*] Writing the C code into gpt.c...")
            write_heuristic_eval(os.path.join(WORK_DIR,"gpt.txt"),os.path.join(WORK_DIR,"gpt.c"),f'{nb_items}')
     
            for i in range(5):
                print(f"[*] Compiling WeightACO_eval_{nb_items}items.c")
                compile(f"WeightACO_eval_{nb_items}items.c",f"WeightACO_eval_{nb_items}items.exe") 
                run_aco(f"WeightACO_eval_{nb_items}items",args=[f"dataset\\mood_val_dataset\\dataset_{i}_instance_{nb_items}_items_3_objectifs.txt"])
            


        print("[*] Extracting Pareto sets from ACO results...")

        #extraire les sets de pareto à partir des résultats de l'ACO
        for (algo_result_file, pareto_output_dir) in val_aco_results:
            extraire_pareto_sets(algo_result_file, pareto_output_dir)

        print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
        #concaténer les sets de pareto extraits pour chaque dataset

        for _,pareto_dir in val_aco_results:
            concatenate_pareto_sets(pareto_dir,1)
        
        print("[*] Calculating  hypervolume and epsilon...")
        #calcul des deux métriques epsilon et hypervolume
        
        
        ##hypervolume
        
        mean_hypervolume_100items =calculate_meanHypervolume(val_pareto_set_files_100items)
        mean_hypervolume_300items =calculate_meanHypervolume(val_pareto_set_files_300items)
        mean_hypervolume_500items =calculate_meanHypervolume(val_pareto_set_files_500items)

        ##epsilon
        mean_epsilon_100items=calculate_meanEpsilon(val_pareto_set_files_100items,val_pareto_ref_files_100items)
        mean_epsilon_300items=calculate_meanEpsilon(val_pareto_set_files_300items,val_pareto_ref_files_300items)
        mean_epsilon_500items=calculate_meanEpsilon(val_pareto_set_files_500items,val_pareto_ref_files_500items)


        copy_folder_to_run_dir(
            source_dir=os.path.join(WORK_DIR, "pareto_set_val"),
            dest_dir=RUN_DIR
        )

        delete_folder(os.path.join(WORK_DIR, "pareto_set_val"))
        for result_file,_ in val_aco_results:
            delete_file(result_file)

        for i in range(population_size):
            delete_folder(os.path.join(WORK_DIR,f"results_individual_{i}")) 
        
        print("[*] moyenne pour hypervolume et  epsilon:")
        
        print(f"[*] Average for hypervolume 100 items: {mean_hypervolume_100items}")
        print(f"[*] Average for epsilon 100 items: {mean_epsilon_100items}")

        print(f"[*] Average for hypervolume 300 items: {mean_hypervolume_300items}")
        print(f"[*] Average for epsilon 300 items: {mean_epsilon_300items}")

        print(f"[*] Average for hypervolume 500 items: {mean_hypervolume_500items}")
        print(f"[*] Average for epsilon 500 items: {mean_epsilon_500items}")

        


