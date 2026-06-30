import subprocess
import sys
import os
import logging 
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

def compile(c_file_name,exe_file_name):
    run_cmd = ["gcc", c_file_name, "gpt.c", "-o", exe_file_name]
    result=subprocess.run(run_cmd,cwd=WORK_DIR)

    if result.returncode!=0:
        print("Erreur de compilation")
    else: print(f"Fichier {c_file_name} compilé avec succès dans {exe_file_name}")
    
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
    run_cmd = [f"./{executable}.exe"] + args
    print(f"Exécution : {' '.join(run_cmd)}")
    
    result = subprocess.run(run_cmd, cwd=WORK_DIR)  
    
    if result.returncode != 0:
        print(f"Erreur à l'exécution (code {result.returncode})")
        sys.exit(1)


if __name__=="__main__":
    input_txt_path="gpt.txt"
    with open(input_txt_path, 'rb') as f:
     raw = f.read()
    idx = raw.find(b'heuristic_v2')
    print(raw[idx-5:idx+20])