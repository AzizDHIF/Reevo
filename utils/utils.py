import subprocess
import logging
import re
import inspect
import shutil
import time
import hydra
import os
import sys
from pathlib import Path


possible_func_names = ["heuristic", "heuristic_v1", "heuristic_v2", "heuristic_v3"]

HEADER_RULES = {
    'math.h': [
        'sqrt', 'pow', 'fabs', 'ceil', 'floor', 'fmod', 'exp', 'log',
        'log2', 'log10', 'sin', 'cos', 'tan', 'atan2', 'round', 'INFINITY', 'NAN',
    ],
    'float.h': [
        'DBL_MAX', 'DBL_MIN', 'FLT_MAX', 'FLT_MIN', 'DBL_EPSILON', 'FLT_EPSILON',
    ],
    'limits.h': [
        'INT_MAX', 'INT_MIN', 'UINT_MAX', 'LONG_MAX', 'LONG_MIN', 'CHAR_MAX',
    ],
    'stdlib.h': [
        'malloc', 'calloc', 'realloc', 'free', 'rand', 'srand', 'abs', 'qsort', 'exit',
    ],
    'string.h': [
        'memset', 'memcpy', 'strcpy', 'strncpy', 'strcmp', 'strncmp', 'strlen', 'strcat',
    ],
    'stdio.h': [
        'printf', 'scanf', 'fprintf', 'sprintf', 'snprintf', 'fopen', 'fclose',
    ],
    'stdbool.h': [
        'bool', 'true', 'false',
    ],
    'stdint.h': [
        'int32_t', 'uint32_t', 'int64_t', 'uint64_t', 'int8_t', 'uint8_t',
    ],
}

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
possible_func_names = ["heuristic", "heuristic_v1", "heuristic_v2", "heuristic_v3"]


def robust_remove(path, retries=10, delay=0.5):
    for _ in range(retries):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
            return True
        except OSError:
            time.sleep(delay)
    return False

def kill_exe(exe_name):
    subprocess.run(["taskkill", "/F", "/T", "/IM", exe_name],
                   capture_output=True)
def print_hyperlink(path, text=None):
    """Print hyperlink to file or folder for convenient navigation"""
    # Format: \033]8;;file:///path/to/file\033\\text\033]8;;\033\\
    text = text or path
    full_path = f"file://{os.path.abspath(path)}"
    return f"\033]8;;{full_path}\033\\{text}\033]8;;\033\\"

def write_heuristic(input_txt_path: str, output_c_path: str) -> None:
   
    with open(input_txt_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Construit un pattern qui matche n'importe quel nom de la liste
    pattern = r'\b(' + '|'.join(re.escape(name) for name in possible_func_names) + r')\b'

    new_content, count = re.subn(pattern, 'heuristic', content)
    if count == 0:
        raise ValueError(
            f"Aucun nom de fonction parmi {possible_func_names} trouvé dans '{input_txt_path}'"
        )
    if '#include "HBACO.h"\n' not in new_content:
            new_content = '#include "HBACO.h"\n' + new_content
    
    with open(output_c_path, 'w', encoding='utf-8') as f:
        f.write(new_content)




def compile(WORK_DIR,c_file_name,exe_file_name):
    run_cmd = ["gcc", c_file_name, "gpt.c", "-o", exe_file_name]

    result=subprocess.run(run_cmd,cwd=WORK_DIR,encoding="utf-8", errors="replace")

    if result.returncode!=0:
        raise RuntimeError("Erreur de compilation")
    
def remove_empty_line(path_file_txt):
    """
    Supprime les lignes vides d'un fichier texte.
    """
    with open(path_file_txt, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    with open(path_file_txt, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip():  # conserve uniquement les lignes non vides
                f.write(line)

def run_aco(WORK_DIR,executable, args=[]):
    exe_path = os.path.join(WORK_DIR, f"{executable}.exe")  # défini EN PREMIER
    run_cmd = [exe_path] + args  # chemin absolu directement dans la commande
    
    try:
        result = subprocess.run(run_cmd, cwd=WORK_DIR, encoding="utf-8", errors="replace")
    except FileNotFoundError as e:
        print(f"[ERREUR] FileNotFoundError : {e}")
        raise

    if result.returncode != 0:
        print(f"Erreur à l'exécution (code {result.returncode})")
        sys.exit(1)
def extraire_pareto_sets(fichier_entree, dossier_sortie,n_dim):
    import os

    os.makedirs(dossier_sortie, exist_ok=True)

    fichier_sortie = None
    compteur = 0

    with open(fichier_entree, 'r', encoding='utf-8', errors='replace') as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue

            if ligne.startswith("mcycle"):
                if fichier_sortie:
                    fichier_sortie.close()
                compteur += 1
                chemin = os.path.join(dossier_sortie, f"pareto_{compteur}.txt")
                fichier_sortie = open(chemin, 'w', encoding='utf-8')
                continue

            
            parties = ligne.split()
            if len(parties) == n_dim:
                try:
                    parties_negatives=[-1*float(x) for x in parties]
                    ligne_negative = "\t".join(str(v) for v in parties_negatives)

                    fichier_sortie.write(ligne_negative + "\n")
                except ValueError:
                    pass

    if fichier_sortie:
        fichier_sortie.close()

    print(f"{compteur} fichiers créés dans '{dossier_sortie}'")




def concatenate_pareto_sets(WORK_DIR,pareto_dir,nb_pareto_files,):
    executable=os.path.join(WORK_DIR,"nondominated")
    result_file = os.path.join(pareto_dir, "final_pareto.txt")

    with open(result_file, "w", encoding='utf-8') as out:
        for j in range(1, nb_pareto_files+1):
            pareto_file = os.path.join(pareto_dir, f"pareto_{j}.txt")

            with open(pareto_file, "r", encoding='utf-8', errors='replace') as f:
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
        cwd=WORK_DIR,
        encoding="utf-8",
        errors="replace"
    )

    if result_filtrage.returncode != 0:
        print(f"Erreur à l'exécution (code {result_filtrage.returncode})")
        sys.exit(1)




def get_profits_range(dataset_path):
    
    
    
    
    with open(dataset_path, "r", encoding="utf-8", errors="replace") as f:
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


            


def calculate_meanHypervolume(WORK_DIR,files):
    
    mean=0
    

    for pareto_file in files:
        if fichier_vide_ou_une_ligne(pareto_file):
            continue 
        
        print("Exécution :", " ".join([os.path.join(WORK_DIR,"hv.exe"), pareto_file,]))

        result_hv = subprocess.run(
            [os.path.join(WORK_DIR,"hv.exe"), pareto_file],
            cwd=WORK_DIR,
            capture_output=True,
            text=True, encoding="utf-8", errors="replace")
        
      
        print(f"Résultat de l'hypervolume pour {pareto_file} : {result_hv.stdout}")


        try:

            mean=mean+float(result_hv.stdout)            
        except ValueError:
            
            print(f"Erreur de conversion pour {pareto_file} : '{result_hv.stdout.strip()}' n'est pas un nombre valide.")
            raise ValueError(f"Erreur de conversion pour {pareto_file} : '{result_hv.stdout.strip()}' n'est pas un nombre valide.")
    
    mean=mean/len(files)
    
    return mean

def calculate_meanEpsilon(WORK_DIR,files, pareto_ref_files):

    
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
            text=True, encoding="utf-8", errors="replace")
        
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


    return mean 

def delete_folder(folder_path):
    if os.path.isdir(folder_path):
        shutil.rmtree(folder_path)

def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)



def vider_dossier(dossier_path):
    """Vide un dossier de tout son contenu (fichiers et sous-dossiers) sans le supprimer lui-même."""
    if not os.path.isdir(dossier_path):
        return  # le dossier n'existe pas, rien à faire

    for nom in os.listdir(dossier_path):
        chemin = os.path.join(dossier_path, nom)
        try:
            if os.path.isfile(chemin) or os.path.islink(chemin):
                os.remove(chemin)
            elif os.path.isdir(chemin):
                shutil.rmtree(chemin)
        except Exception as e:
            print(f"Impossible de supprimer {chemin} : {e}")

def get_pareto_ref_etendue(pareto_ref_path):
    points = []
    with open(pareto_ref_path, "r", encoding="utf-8", errors="replace") as f:
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
    with open(chemin_fichier, 'r', encoding='utf-8', errors='replace') as f:
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
def write_heuristic_on_txt(WORK_DIR,file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    start_marker = "```c"
    end_marker = "```"

    start_index = content.find(start_marker)
    if start_index == -1:
        raise ValueError("Bloc de code C non trouvé (marqueur ```c manquant).")
    start_index += len(start_marker)

    end_index = content.find(end_marker, start_index)
    if end_index == -1:
        raise ValueError("Bloc de code C non fermé (marqueur ``` de fin manquant).")

    c_code = content[start_index:end_index].strip()

    c_code = normalize_heuristic_signature(c_code)

    with open(os.path.join(WORK_DIR, "gpt.txt"), "w", encoding='utf-8') as f:
        f.write('#include "HBACO.h" \n')
        f.write(c_code)


def normalize_heuristic_signature(c_code: str) -> str:
    """
    Force la signature de la fonction heuristique générée à utiliser
    des pointeurs (double**, double*, int*) plutôt que des tableaux
    à taille fixe (double[dimension][NBITEMS], etc.), quel que soit
    le format produit par le LLM. Le corps de la fonction n'est pas
    modifié, seule la ligne de signature l'est.
    """
    pattern = r'double\s+(' + '|'.join(re.escape(name) for name in possible_func_names) + r')\s*\(.*?\)\s*\{'

    def replace_signature(match):
        func_name = match.group(1)
        return (
            f'double {func_name}(int index_item, double **weights, double *capacity, '
            f'int nb_voisinage, int *voisinage, double *profit) {{'
        )

    new_code, count = re.subn(pattern, replace_signature, c_code, count=1, flags=re.DOTALL)

    if count == 0:
        raise ValueError(
            f"Signature de fonction heuristique introuvable ou non conforme parmi {possible_func_names} "
            "pour normalisation."
        )

    return new_code

def rename_heuristic(content: str) -> str:
    

    # Pattern qui matche n'importe quel nom de la liste
    pattern = r'\b(' + '|'.join(re.escape(name) for name in possible_func_names) + r')\b'

    new_content, count = re.subn(pattern, 'heuristic', content)
    if count == 0:
        raise ValueError(
            f"Aucun nom de fonction parmi {possible_func_names} trouvé dans le contenu fourni"
        )

    if '#include "HBACO.h"\n' not in new_content:
        new_content = '#include "HBACO.h"\n' + new_content

    return new_content
def init_client(cfg):
    global client
    if cfg.get("model", None): # for compatibility
        model: str = cfg.get("model")
        temperature: float = cfg.get("temperature", 1.0)
        if model.startswith("gpt"):
            from utils.llm_client.openai import OpenAIClient
            client = OpenAIClient(model, temperature)
        elif cfg.model.startswith("GLM"):
            from utils.llm_client.zhipuai import ZhipuAIClient
            client = ZhipuAIClient(model, temperature)
        else: # fall back to Llama API
            from utils.llm_client.llama_api import LlamaAPIClient
            client = LlamaAPIClient(model, temperature)
    else:
        client = hydra.utils.instantiate(cfg.llm_client)
    return client
    
import glob

def sweep(work_dir):
    
    kill_exe("WeightACO_*.exe")          # taskkill accepte le joker *
    for p in glob.glob(os.path.join(work_dir, "results_individual_*")):
        robust_remove(p)
    for p in glob.glob(os.path.join(work_dir, "WeightACO_*.exe")):
        robust_remove(p)
    for p in glob.glob(os.path.join(work_dir, "results_val_dataset_*.txt")):
        robust_remove(p)
    robust_remove(os.path.join(work_dir, "pareto_set_val"))
def cleanup_individual(work_dir,response_id):
    
    exe = f"WeightACO_train_100items_results_individual_{response_id}.exe"
    kill_exe(exe)
    robust_remove(os.path.join(work_dir, exe))
    robust_remove(os.path.join(work_dir, f"results_individual_{response_id}"))
def file_to_string(filename):
    with open(filename, 'r', encoding="utf-8", errors="replace") as file:
        return file.read()
    
    
def print_hyperlink(path, text=None):
    """Print hyperlink to file or folder for convenient navigation"""
    # Format: \033]8;;file:///path/to/file\033\\text\033]8;;\033\\
    text = text or path
    full_path = f"file://{os.path.abspath(path)}"
    return f"\033]8;;{full_path}\033\\{text}\033]8;;\033\\"


def filter_traceback(s):
    lines = s.split('\n')
    filtered_lines = []
    for i, line in enumerate(lines):
        if line.startswith('Traceback'):
            for j in range(i, len(lines)):
                if "Set the environment variable HYDRA_FULL_ERROR=1" in lines[j]:
                    break
                filtered_lines.append(lines[j])
            return '\n'.join(filtered_lines)
    return ''  # Return an empty string if no Traceback is found

def block_until_running(stdout_filepath, log_status=False, iter_num=-1, response_id=-1):
    # Ensure that the evaluation has started before moving on
    while True:
        log = file_to_string(stdout_filepath)
    
        if "[*] Running ACO on training datasets..." in log:
    
            if log_status and "Traceback" in log:
                logging.info(f"Iteration {iter_num}: Code Run {response_id} execution error!")
            else:
                logging.info(f"Iteration {iter_num}: Code Run {response_id} started")
            break
        if "Traceback" in log:
            logging.warning(
                f"Iteration {iter_num}: Code Run {response_id} crashed early!  "
            )
            break
        time.sleep(1)



def robust_remove(path, retries=10, delay=0.5):
    for _ in range(retries):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
            return True
        except OSError:
            time.sleep(delay)
    return False

def kill_exe(exe_name):
    subprocess.run(["taskkill", "/F", "/T", "/IM", exe_name],
                   capture_output=True)

"""def extract_description(response: str) -> tuple[str, str]:
    # Regex patterns to extract code description enclosed in GPT response, it starts with ‘<start>’ and ends with ‘<end>’
    pattern_desc = [r'<start>(.*?)```python', r'<start>(.*?)<end>']
    for pattern in pattern_desc:
        desc_string = re.search(pattern, response, re.DOTALL)
        desc_string = desc_string.group(1).strip() if desc_string is not None else None
        if desc_string is not None:
            break
    return desc_string"""



def extract_c_code_from_generator(content):
    """Extract C heuristic function from the response of the code generator."""
    
    # 1. Cherche dans un bloc ```c ... ```
    pattern_code = r'```c(.*?)```'
    code_string = re.search(pattern_code, content, re.DOTALL)
    code_string = code_string.group(1).strip() if code_string is not None else None
    code_string = rename_heuristic(code_string) if code_string is not None else None
    if code_string is None:
        # 2. Cherche la signature de la fonction directement dans le contenu
        lines = content.split('\n')
        lines=[l.strip() for l in lines]
        start = None
        brace_count = 0
        end = None

        for i, line in enumerate(lines):
            # Détecte le début de la fonction via sa signature
            if 'double heuristic(' in line:
                start = i
            
            # Compte les accolades pour trouver la fin du bloc
            if start is not None:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '{' in '\n'.join(lines[start:i+1]):
                    end = i
                    break

        if start is not None and end is not None:
            code_string = '\n'.join(lines[start:end+1])

    if code_string is None:
        return None

    # 3. Ajoute les includes nécessaires (détection par mot entier, pas substring)
    needed_headers = []
    for header, symbols in HEADER_RULES.items():
        for symbol in symbols:
            if re.search(r'\b' + re.escape(symbol) + r'\b', code_string):
                needed_headers.append(header)
                break  # un seul symbole trouvé suffit pour ajouter ce header

    includes = '\n'.join(f'#include <{h}>' for h in needed_headers)
    code_string =  (includes + '\n' if includes else '') + code_string
    
    if '#include "HBACO.h"\n' not in code_string:
        code_string = '#include "HBACO.h"\n' + code_string
    return code_string

def filter_code(code_string):
    """Remove lines containing signature and include statements."""
    lines = code_string.split('\n')
    lines=[l.strip() for l in lines]
    filtered_lines = []

    # Enlever les includes
    lines = [line for line in lines if not line.startswith('#include')]

    # Trouver la première accolade et garder tout ce qui est après
    first_brace = None
    for i, line in enumerate(lines):
        if '{' in line:
             # Tronquer la ligne pour commencer au '{'
            lines[i] = line[line.index('{'):]
            first_brace = i
            break
    
    if first_brace is not None:
        filtered_lines = lines[first_brace:]

    return '\n'.join(filtered_lines)

def get_last_n_lines(file_path,nb_lines):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    return [line.rstrip("\n") for line in lines[-nb_lines:]]

import re
import matplotlib.pyplot as plt

import re
import numpy as np
import matplotlib.pyplot as plt

def plot_results_different_algos(results_by_algo):
    """
    results_by_algo : dictionnaire
        clé   = nom de l'algo (str)
        valeur = liste de chaînes contenant les moyennes
    """

    dataset_labels = ["dataset_100 items", "dataset_300 items"]

    def extract_values(lines):
        hv_100 = hv_300 = eps_100 = eps_300 = None

        for line in lines:
            match = re.search(
                r'Average for hypervolume for dataset (\d+) items:\s*([0-9.eE+-]+)',
                line
            )
            if match:
                items = int(match.group(1))
                value = float(match.group(2))
                if items == 100:
                    hv_100 = value
                elif items == 300:
                    hv_300 = value

            match = re.search(
                r'Average for epsilon for dataset (\d+) items:\s*([0-9.eE+-]+)',
                line
            )
            if match:
                items = int(match.group(1))
                value = float(match.group(2))
                if items == 100:
                    eps_100 = value
                elif items == 300:
                    eps_300 = value

        return hv_100, hv_300, eps_100, eps_300

    # Une couleur différente par algo
    color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    colors = {
        algo_name: color_cycle[i % len(color_cycle)]
        for i, algo_name in enumerate(results_by_algo.keys())
    }

    def make_plot(metric, ylabel, title):
        plt.figure(figsize=(10, 6))

        n_algos = len(results_by_algo)
        x = np.arange(len(dataset_labels))      # positions des groupes
        bar_width = 0.8 / n_algos               # largeur d'une barre

        for i, (algo_name, lines) in enumerate(results_by_algo.items()):
            hv_100, hv_300, eps_100, eps_300 = extract_values(lines)

            if metric == "hypervolume":
                values = [hv_100, hv_300]
            else:
                values = [eps_100, eps_300]

            # None -> NaN pour ne pas faire planter plt.bar si une valeur manque
            values = [np.nan if v is None else v for v in values]

            # Décalage pour centrer le groupe de barres sur chaque dataset
            offset = (i - (n_algos - 1) / 2) * bar_width

            plt.bar(
                x + offset,
                values,
                width=bar_width,
                color=colors[algo_name],
                label=algo_name
            )

        plt.xticks(x, dataset_labels)
        plt.xlabel("Dataset")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, axis="y", alpha=0.3)
        plt.gca().set_axisbelow(True)

        plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        plt.tight_layout()
        plt.show()

    make_plot("hypervolume", "Hypervolume", "Hypervolume across algorithms")
    make_plot("epsilon", "Epsilon", "Epsilon across algorithms")
def plot_results(results):
    """
    results : dictionnaire
        clé   = nombre d'itérations (int)
        valeur = liste de chaînes contenant les moyennes
    """

    hypervolume_100 = []
    hypervolume_300 = []
    epsilon_100 = []
    epsilon_300 = []

    iterations = sorted(results.keys())

    for iteration in iterations:
        lines = results[iteration]

        hv_100 = hv_300 = eps_100 = eps_300 = None

        for line in lines:

            # Hypervolume
            match = re.search(
                r'Average for hypervolume for dataset (\d+) items:\s*([0-9.eE+-]+)',
                line
            )

            if match:
                items = int(match.group(1))
                value = float(match.group(2))

                if items == 100:
                    hv_100 = value
                elif items == 300:
                    hv_300 = value

            # Epsilon
            match = re.search(
                r'Average for epsilon for dataset (\d+) items:\s*([0-9.eE+-]+)',
                line
            )

            if match:
                items = int(match.group(1))
                value = float(match.group(2))

                if items == 100:
                    eps_100 = value
                elif items == 300:
                    eps_300 = value

        hypervolume_100.append(hv_100)
        hypervolume_300.append(hv_300)
        epsilon_100.append(eps_100)
        epsilon_300.append(eps_300)

    # --------------------------------------------------
    # Fonction pour régler automatiquement l'axe Y
    # --------------------------------------------------

    def set_y_scale(values):
        valid_values = [v for v in values if v is not None]

        if not valid_values:
            return

        min_value = min(valid_values)
        max_value = max(valid_values)

        # Cas où toutes les valeurs sont identiques
        if min_value == max_value:
            margin = abs(min_value) * 0.1

            if margin == 0:
                margin = 1

        else:
            margin = (max_value - min_value) * 0.1

        plt.ylim(
            min_value - margin,
            max_value + margin
        )

    # ==================================================
    # 1. Hypervolume - 100 items
    # ==================================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        hypervolume_100,
        marker="o"
    )

    plt.xlabel("Nombre maximal d'évaluations")
    plt.ylabel("Hypervolume")
    plt.title("Hypervolume - Dataset 100 items")

    set_y_scale(hypervolume_100)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ==================================================
    # 2. Hypervolume - 300 items
    # ==================================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        hypervolume_300,
        marker="o"
    )

    plt.xlabel("Nombre maximal d'évaluations")
    plt.ylabel("Hypervolume")
    plt.title("Hypervolume - Dataset 300 items")

    set_y_scale(hypervolume_300)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ==================================================
    # 3. Epsilon - 100 items
    # ==================================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        epsilon_100,
        marker="o"
    )

    plt.xlabel("Nombre maximal d'évaluations")
    plt.ylabel("Epsilon")
    plt.title("Epsilon - Dataset 100 items")

    set_y_scale(epsilon_100)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ==================================================
    # 4. Epsilon - 300 items
    # ==================================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        epsilon_300,
        marker="o"
    )

    plt.xlabel("Nombre maximal d'évaluations")
    plt.ylabel("Epsilon")
    plt.title("Epsilon - Dataset 300 items")

    set_y_scale(epsilon_300)

    plt.grid(True)
    plt.tight_layout()
    plt.show()




def plot_results_big_dataset_version(results):
    """
    results : dictionnaire
        clé    = nombre d'itérations (int)
        valeur = liste de chaînes contenant les métriques Hypervolume/Epsilon
    """

    # Regex : capture le type de métrique, le chemin du dataset, et la valeur
    pattern = re.compile(
        r'^\[\*\]\s*(Hypervolume|Epsilon)\s*for\s*dataset\s+(.+):\s+'
        r'([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$'
    )

    # Regex pour extraire un nom court de dataset depuis le chemin
    # ex: ...pareto_sets_dataset_250_2\final_pareto.txt_dat -> "250_2"
    dataset_name_pattern = re.compile(r'pareto_sets_dataset_([^\\]+)\\')

    iterations = sorted(results.keys())

    # data[dataset_name][metric] = liste de valeurs (alignée sur `iterations`)
    data = {}

    for iteration in iterations:
        lines = results[iteration]

        # valeurs trouvées pour cette itération : {(dataset, metric): value}
        current = {}

        for line in lines:
            match = pattern.match(line)
            if not match:
                continue

            metric, path, value_str = match.groups()
            value = float(value_str)

            name_match = dataset_name_pattern.search(path)
            dataset_name = name_match.group(1) if name_match else path

            current[(dataset_name, metric)] = value

        # on met à jour data en gardant l'alignement avec `iterations`
        # (None si la valeur est absente pour cette itération)
        all_keys = {k for k in current.keys()}
        for dataset_name, metric in all_keys:
            data.setdefault(dataset_name, {}).setdefault(metric, [])

        # s'assurer que toutes les séries existantes reçoivent une valeur
        # (même None) à cette itération, pour rester alignées
        for dataset_name, metrics in data.items():
            for metric, series in metrics.items():
                series.append(current.get((dataset_name, metric)))

    # --------------------------------------------------
    # Fonction pour régler automatiquement l'axe Y
    # --------------------------------------------------

    def set_y_scale(values):
        valid_values = [v for v in values if v is not None]

        if not valid_values:
            return

        min_value = min(valid_values)
        max_value = max(valid_values)

        if min_value == max_value:
            margin = abs(min_value) * 0.1
            if margin == 0:
                margin = 1
        else:
            margin = (max_value - min_value) * 0.1

        plt.ylim(min_value - margin, max_value + margin)

    # --------------------------------------------------
    # Un plot par (dataset, métrique)
    # --------------------------------------------------

    dataset_names = sorted(data.keys())

    for dataset_name in dataset_names:
        for metric in ("Hypervolume", "Epsilon"):
            series = data[dataset_name].get(metric)
            if series is None:
                continue

            plt.figure(figsize=(10, 6))
            plt.plot(iterations, series, marker="o")

            plt.xlabel("Nombre maximal d'évaluations")
            plt.ylabel(metric)
            plt.title(f"{metric} - Dataset {dataset_name}")

            set_y_scale(series)

            plt.grid(True)
            plt.tight_layout()
            plt.show()
def make_dictionnary_results(paths):
  

    results = {}
    iterations = [25, 50, 75, 100]
    for path,iter in zip(paths, iterations):
        l=get_last_n_lines(path, 4)
        results[iter] = l
    print(results)
       
    return results



def get_lines_with_metrics(path):

    pattern = re.compile(

    r'^\[\*\]\s+(?:Epsilon|Hypervolume)\s+for dataset\s+.+:\s+[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\s*$'
    )

    matching_lines = []
    with open(path, 'r', encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip('\n')
            if pattern.match(line):
                matching_lines.append(line)
   
    return matching_lines


def make_dictionnary_results_big_dataset_version(paths):
  

    results = {}
    iterations = [25, 50, 75, 100]
    for path,iter in zip(paths, iterations):
        l=get_lines_with_metrics(path)
        results[iter] = l
    
       
    return results

def make_dictionnary_results_by_algo(paths,algo_names):
    """
    results_by_algo : dictionnaire
        clé   = nom de l'algo (str)
        valeur = dictionnaire results de cet algo
                 clé   = nombre d'itérations (int)
                 valeur = liste de chaînes contenant les moyennes
    """
    
    results_by_algo = {}
    for path,algo_name in zip(paths, algo_names):
        l=get_last_n_lines(path, 4)
        results_by_algo[algo_name] = l
    return results_by_algo

def get_code_path(execution_directory):
    log_file=os.path.join(execution_directory,"mo_mkp_aco-aco.log")
    
    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
     text = f.read()

    m = re.search(r"Best Code Path Overall:.*?file://(.+?\.txt)", text)

    if m:
        best_code_path = m.group(1)
        return best_code_path
        # C:\Reevo\outputs\mo_mkp_aco-aco\2026-09-07_11-03-56\problem_iter3_response1.txt
    else:
        best_code_path = None
        print("Chemin non trouvé dans le fichier.")


if __name__ == "__main__":
    # Test de la fonction extract_c_code_from_generator
    test_strings = """```c
double heuristic_v2(int index_item, double **weights, double *capacity, int nb_voisinage, int *voisinage, double *profit) {
    double h=0;
    double variance = 0;
    for(int j=0; j<dimension;j++) {
        h = h + weights[j][voisinage[index_item]]/capacity[j]; 
        variance += weights[j][voisinage[index_item]]*weights[j][voisinage[index_item]];
    }
    
    double diversity_factor = sqrt(variance / dimension);
    
    return diversity_factor > 0 ? profit[voisinage[index_item]]/h : 0;
}
```
"""
    print("=== Test de la fonction extract_c_code_from_generator ===")
    print(extract_c_code_from_generator(test_strings))