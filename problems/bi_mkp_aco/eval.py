import subprocess
import sys
import os
import logging
from pathlib import Path
import shutil
import time 
RUN_DIR = Path(os.getcwd())  # dossier créé par Hydra pour cette exécution
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"C:\Reevo")
from utils.utils import *
import re

import sys
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if __name__ == "__main__":
    print("[*] Running ...")
    mood = sys.argv[2]

    datasets = [
        "dataset\\mood_train_dataset\\dataset_0_instance_100_items_2_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_1_instance_100_items_2_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_2_instance_100_items_2_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_3_instance_100_items_2_objectifs.txt",
        "dataset\\mood_train_dataset\\dataset_4_instance_100_items_2_objectifs.txt",
    ]
    
    
    print(f"[*] Mood: {mood}")
    assert mood in ["train", "val","final_val"]


    if mood == 'train':

        try:
            start_time_train=time.perf_counter()
            id_response=f"results_individual_{sys.argv[1]}"
            vider_dossier(os.path.join(WORK_DIR,id_response))
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
            
            
            write_heuristic(os.path.join(WORK_DIR,"gpt.c"),os.path.join(WORK_DIR,"gpt.c"))

            compile(WORK_DIR,"WeightACO.c",f"WeightACO_train_100items_{id_response}.exe")

            #lancer l'ACO sur les datasets du train
            print("[*] Running ACO on training datasets...")

            for dataset,res_file in zip(datasets,result_files):
                run_aco(WORK_DIR,f"WeightACO_train_100items_{id_response}",args=[dataset, res_file])

            print("[*] Extracting Pareto sets from ACO results...")

            #extraire les sets de pareto à partir des résultats de l'ACO
            for (algo_result_file, pareto_output_dir) in aco_results:
                extraire_pareto_sets(algo_result_file, pareto_output_dir,2)
            
            print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
            #concaténer les sets de pareto extraits pour chaque dataset

            for pareto_dir in pareto_set_dirs:
                concatenate_pareto_sets(WORK_DIR,pareto_dir,2)
                      
            print("[*] Calculating  hypervolume and epsilon...")
            #calcul des deux métriques epsilon et hypervolume
            
            ##hypervolume
            mean_hypervolume=calculate_meanHypervolume(WORK_DIR,pareto_set_files)
            ##epsilon
            mean_epsilon=calculate_meanEpsilon(WORK_DIR,pareto_set_files,pareto_ref_files)
            metric=sys.argv[3]
            assert metric in ["hypervolume","epsilon"]
            elapsed_train = time.perf_counter() - start_time_train
            print(f"execution time for evaluation : {elapsed_train:.2f} seconds ({elapsed_train/60:.2f} minutes)")
                         
            if metric=="hypervolume":
                print("[*] moyenne pour hypervolume :")
                
                print(mean_hypervolume)
            else:
                print("[*] moyenne pour epsilon :")
                        
                print(mean_epsilon)

          

        finally:
            #Supprimer les dossiers de sets de pareto temporaire
            
            try:
                delete_folder(os.path.join(WORK_DIR,f"{id_response}"))
            
            except Exception as e:
                logging.warning(f"Failed to delete {id_response} :  {e}")

            try:
                delete_file(os.path.join(WORK_DIR,f"WeightACO_train_100items_{id_response}.exe"))
            except Exception as e:
                    logging.warning(f"Failed to delete WeightACO_train_100items_{id_response}.exe: {e}")

            
                    
         
    

        


   
    
    elif mood == 'val':
        try:
            start_time_eval = time.perf_counter() 
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
                    (os.path.join(WORK_DIR,"results_val_dataset_4_300_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_4_items_300")),]
                    #(os.path.join(WORK_DIR,"results_val_dataset_0_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_0_items_500")),
                    #(os.path.join(WORK_DIR,"results_val_dataset_1_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_1_items_500")),
                    #(os.path.join(WORK_DIR,"results_val_dataset_2_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_2_items_500")),
                    #(os.path.join(WORK_DIR,"results_val_dataset_3_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_3_items_500")),
                    #(os.path.join(WORK_DIR,"results_val_dataset_4_500_items.txt"), os.path.join(WORK_DIR,"pareto_set_val\\pareto_sets_dataset_4_items_500")),]
            
            
            val_pareto_ref_files_100items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_100_items\\final_pareto_file.txt_dat") for i in range(5)]
            val_pareto_ref_files_300items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_300_items\\final_pareto_file.txt_dat") for i in range(5)]
            val_pareto_ref_files_500items=[os.path.join(WORK_DIR,f"dataset\\mood_val_dataset\\ref_dataset_{i}_500_items\\final_pareto_file.txt_dat") for i in range(5)]
            val_pareto_set_files=[os.path.join(p, "final_pareto.txt_dat") for _,p in val_aco_results]
            val_pareto_set_files_100items=[f for f  in  val_pareto_set_files if "items_100" in f] 
            val_pareto_set_files_300items=[f for f  in  val_pareto_set_files if "items_300" in f]
            val_pareto_set_files_500items=[f for f  in  val_pareto_set_files if "items_500" in f]
            
        
            print("[*] Running ACO on EVAL datasets...")

            #lancer l'ACO sur les datasets du train


                    
            for nb_items in [100,300]:
                
                print("[*] Writing the C code into gpt.c...")
                
        
                for i in range(5):
                    print(f"[*] Compiling WeightACO.c")
                    write_heuristic(os.path.join(WORK_DIR,"gpt.c"),os.path.join(WORK_DIR,"gpt.c"))

                    compile(WORK_DIR,f"WeightACO.c",f"WeightACO_eval_{nb_items}items.exe") 
                    run_aco(WORK_DIR,f"WeightACO_eval_{nb_items}items",args=[f"dataset\\mood_val_dataset\\dataset_{i}_instance_{nb_items}_items_2_objectifs.txt"])
                


            print("[*] Extracting Pareto sets from ACO results...")

            #extraire les sets de pareto à partir des résultats de l'ACO
            for (algo_result_file, pareto_output_dir) in val_aco_results:
                extraire_pareto_sets(algo_result_file, pareto_output_dir,2)

            print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
            #concaténer les sets de pareto extraits pour chaque dataset

            for _,pareto_dir in val_aco_results:
                concatenate_pareto_sets(WORK_DIR,pareto_dir,2)
            
            print("[*] Calculating  hypervolume and epsilon...")
            #calcul des deux métriques epsilon et hypervolume
            
            
            ##hypervolume
            
            mean_hypervolume_100items =calculate_meanHypervolume(WORK_DIR,val_pareto_set_files_100items)
            mean_hypervolume_300items =calculate_meanHypervolume(WORK_DIR,val_pareto_set_files_300items)
            #mean_hypervolume_500items =calculate_meanHypervolume(WORK_DIR,val_pareto_set_files_500items)
            mean_epsilon_100items =calculate_meanEpsilon(WORK_DIR,val_pareto_set_files_100items,val_pareto_ref_files_100items)
            mean_epsilon_300items =calculate_meanEpsilon(WORK_DIR,val_pareto_set_files_300items,val_pareto_ref_files_300items)
            #mean_epsilon_500items =calculate_meanEpsilon(WORK_DIR,val_pareto_set_files_500items,val_pareto_ref_files_500items)
            copy_folder_to_run_dir(
                source_dir=os.path.join(WORK_DIR, "pareto_set_val"),
                dest_dir=RUN_DIR
            )

            elapsed_eval = time.perf_counter() - start_time_eval
            print(f"execution time for evaluation : {elapsed_eval:.2f} seconds ({elapsed_eval/60:.2f} minutes)")
                        
            
            print("[*] Average for hypervolume and epsilon:")
            
            print(f"[*] Average for hypervolume for dataset 100 items: {mean_hypervolume_100items}")
            print(f"[*] Average for epsilon for dataset 100 items: {mean_epsilon_100items}")

            print(f"[*] Average for hypervolume for dataset 300 items: {mean_hypervolume_300items}")
            print(f"[*] Average for epsilon for dataset 300 items: {mean_epsilon_300items}")

            #print(f"[*] Average for hypervolume for dataset 500 items: {mean_hypervolume_500items}")
            #print(f"[*] Average for epsilon for dataset 500 items: {mean_epsilon_500items}")
            
            
        
        
        finally:
            delete_folder(os.path.join(WORK_DIR, "pareto_set_val"))
            for result_file,_ in val_aco_results:
                try: delete_file(result_file)
                except Exception as e:
                    logging.warning(f"Failed to delete {result_file}: {e}")

            
            for nb_items in [100,300]:
                try:
                    delete_file(os.path.join(WORK_DIR,f"WeightACO_eval_{nb_items}items.exe"))
                except Exception as e:
                    logging.warning(f"Failed to delete WeightACO_eval_{nb_items}items.exe: {e}")
           
            for i in range(20): # we assume the maximum pop ulation size is 20
               
                delete_folder(os.path.join(WORK_DIR,f"results_individual_{i}"))
                delete_file(os.path.join(WORK_DIR,f"WeightACO_train_100items_results_individual_{i}.exe"))

