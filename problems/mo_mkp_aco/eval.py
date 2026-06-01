import subprocess
import sys
import os
WORK_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier du script Python

def compile(c_file="WeightACO_train.c",executable="WeightACO_train"):
    # Compilation
    compile_cmd = ["gcc", c_file, "-o", executable, "-lm"]
    print(f"Compilation : {' '.join(compile_cmd)}")
    
    result = subprocess.run(compile_cmd, capture_output=True, text=True,cwd=WORK_DIR)
    
    if result.returncode != 0:
        print("Erreur de compilation :")
        print(result.stderr)
        sys.exit(1)
    
    print("Compilation réussie !\n")

def   run(executable="WeightACO_train", args=[]):
    # Exécution
    run_cmd = [f"./{executable}.exe"] + args
    print(f"Exécution : {' '.join(run_cmd)}")
    
    result = subprocess.run(run_cmd, cwd=WORK_DIR, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Erreur à l'exécution :")
        print(result.stderr)
        sys.exit(1)
    
    print("Sortie du programme :")
    print(result.stdout)

if __name__ == "__main__":
    
    args = [["dataset_0_instance_100_items_3_objectifs.txt"], ["dataset_1_instance_100_items_3_objectifs.txt"], ["dataset_2_instance_100_items_3_objectifs.txt"], ["dataset_3_instance_100_items_3_objectifs.txt"], ["dataset_4_instance_100_items_3_objectifs.txt"]]
    compile()
    for arg in args :
      run(args=arg)