import logging
import re
import inspect
import hydra
import os
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
    

def file_to_string(filename):
    with open(filename, 'r', encoding="utf-8") as file:
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
    with open(file_path, "r", encoding="cp1252") as f:
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
    with open(path, 'r', encoding="cp1252") as f:
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
    
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
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