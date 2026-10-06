from unittest import result

import hydra
import logging 
import os
from pathlib import Path
import subprocess
from utils.utils import make_dictionnary_results_big_dataset_version,get_code_path, init_client, plot_results_big_dataset_version, plot_results_different_algos, print_hyperlink, plot_results, make_dictionnary_results,make_dictionnary_results_by_algo
import sys
import yaml 
import time
ROOT_DIR = os.getcwd()
logging.basicConfig(level=logging.INFO)
if sys.argv[1]=="plot_results":
    plot_results(make_dictionnary_results([r"outputs\mo_mkp_aco-aco\2026-09-08_21-39-00\best_code_overall_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_22-53-50\best_code_overall_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-09_00-07-23\best_code_overall_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-09_01-34-37\best_code_overall_val_stdout.txt"]))




if sys.argv[1]=="plot_results_different_algos":

    plot_results_different_algos(make_dictionnary_results_by_algo([r"problems\mo_mkp_aco\basic_heuristic_evaluation\metric_of_basic_heuristic.txt",r"outputs\mo_mkp_aco-aco\2026-09-09_01-34-37\best_code_overall_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_17-55-03\best_code_overall_val_stdout.txt"]))




if sys.argv[1]=="plot_results_big_dataset_version":

    plot_results_big_dataset_version(make_dictionnary_results_big_dataset_version([r"outputs\mo_mkp_aco-aco\2026-09-07_11-03-56\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-07_11-45-13\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-07_12-37-37\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-07_14-17-29\best_code_overall_final_val_stdout.txt"]))

    plot_results_big_dataset_version(make_dictionnary_results_big_dataset_version([r"outputs\mo_mkp_aco-aco\2026-09-07_19-40-33\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-07_20-01-30\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-07_21-18-50\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_01-41-58\best_code_overall_final_val_stdout.txt"]))

    plot_results_big_dataset_version(make_dictionnary_results_big_dataset_version([r"outputs\mo_mkp_aco-aco\2026-09-08_10-38-37\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_11-27-11\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_12-21-03\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_17-55-03\best_code_overall_final_val_stdout.txt"]))

    plot_results_big_dataset_version(make_dictionnary_results_big_dataset_version([r"outputs\mo_mkp_aco-aco\2026-09-08_21-39-00\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-08_22-53-50\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-09_00-07-23\best_code_overall_final_val_stdout.txt",r"outputs\mo_mkp_aco-aco\2026-09-09_01-34-37\best_code_overall_final_val_stdout.txt"]))






if sys.argv[1]=="final_eval":

    execution_directories=[r"outputs\mo_mkp_aco-aco\2026-09-08_11-27-11"]
    code_paths=[get_code_path(i) for i in execution_directories]
    
    workspace_dir = Path.cwd()
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    test_script = f"{ROOT_DIR}/problems/mo_mkp_aco/eval.py"
    for directory_path,best_code_path in zip(execution_directories,code_paths):
        test_script_stdout=os.path.join(directory_path,"best_code_overall_final_val_stdout.txt")
        logging.info(f"Running final validation script...: {print_hyperlink(test_script)}")
        start_time_eval = time.perf_counter() 
    
        with open(test_script_stdout, 'w', encoding="utf-8") as stdout:
            result=subprocess.run([sys.executable, test_script, "-1", "final_val",best_code_path,directory_path ], stdout=stdout,stderr=subprocess.PIPE,text=True,check=False )
        elapsed_eval = time.perf_counter() - start_time_eval  # <-- fin du chrono
        logging.info(f"execution time for evaluation of {directory_path} : {elapsed_eval:.2f} seconds ({elapsed_eval/60:.2f} minutes)")

        if result.returncode != 0:
            logging.error(
                f"Le script de validation a échoué (code retour {result.returncode}).\n"
                f"STDERR:\n{result.stderr}\n"
                f"Voir aussi la sortie standard : {print_hyperlink(test_script_stdout)}"
            )
            # Optionnel : relancer l'exception pour stopper l'exécution
            raise RuntimeError(
                f"Validation script failed with code {result.returncode}. STDERR:\n{result.stderr}"
            )
        else:
            logging.info(f"Validation script finished. Results are saved in {print_hyperlink(test_script_stdout)}.")

        
        # Print the results
        with open(test_script_stdout, 'r', encoding="cp1252") as file:
            for line in file.readlines():
                logging.info(line.strip())
            
