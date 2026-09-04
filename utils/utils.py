import logging
import re
import inspect
import hydra
import os
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
    code_string = '#include "HBACO.h"\n' + (includes + '\n' if includes else '') + code_string
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

def plot_results_boxplot(results_by_algo):
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

        for algo_name, lines in results_by_algo.items():
            hv_100, hv_300, eps_100, eps_300 = extract_values(lines)

            if metric == "hypervolume":
                values = [hv_100, hv_300]
            else:
                values = [eps_100, eps_300]

            plt.plot(
                dataset_labels,
                values,
                marker="o",
                linestyle="None",
                color=colors[algo_name],
                label=algo_name
            )

        plt.xlabel("Dataset")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True)

        plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        plt.tight_layout()
        plt.show()

    make_plot("hypervolume", "Hypervolume", "Hypervolume par algo")
    make_plot("epsilon", "Epsilon", "Epsilon par algo")
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

def make_dictionnary_results(paths):
  

    results = {}
    iterations = [25, 50, 75, 100]
    for path,iter in zip(paths, iterations):
        l=get_last_n_lines(path, 4)
        results[iter] = l

       
    return results

def make_dictionnary_results_by_algo(paths):
    """
    results_by_algo : dictionnaire
        clé   = nom de l'algo (str)
        valeur = dictionnaire results de cet algo
                 clé   = nombre d'itérations (int)
                 valeur = liste de chaînes contenant les moyennes
    """
    algo_names=["GW-ACO_classique", "reevo_25_func_evals", "reevo_50_func_evals", "reevo_75_func_evals", "reevo_100_func_evals"]
    results_by_algo = {}
    for path,algo_name in zip(paths, algo_names):
        l=get_last_n_lines(path, 4)
        results_by_algo[algo_name] = l
    return results_by_algo