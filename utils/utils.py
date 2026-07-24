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

