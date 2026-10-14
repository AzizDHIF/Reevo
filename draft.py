    #mood = final_val:
    if sys.argv[1]=="final_eval":
    
        try:
            
            run_directory=sys.argv[4]
            
            logging.info(f"[*] Final Evaluating for execution ")
            os.makedirs(os.path.join(WORK_DIR,"pareto_set_final_val"), exist_ok=True)
            from itertools import product
            val_aco_results=[(os.path.join(WORK_DIR,"results_final_val_dataset_250_2.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_250_2")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_250_3.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_250_3")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_500_2.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_500_2")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_500_4.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_500_4")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_750_2.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_750_2")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_750_3.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_750_3")),
                             (os.path.join(WORK_DIR,"results_final_val_dataset_750_4.txt"), os.path.join(WORK_DIR,"pareto_set_final_val\\pareto_sets_dataset_750_4"))]
                 
            
            val_pareto_ref_files=[os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_250.2.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_250.3.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_500.2.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_500.4.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_750.2.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_750.3.txt_dat"),
                                  os.path.join(WORK_DIR,"dataset\\mood_final_val_dataset\\pareto_final_result_750.4.txt_dat")]

            
            val_pareto_set_files=[os.path.join(p, "final_pareto.txt_dat") for _,p in val_aco_results]
            print("[*] Running ACO on EVAL datasets...")

            #lancer l'ACO sur les datasets du train

     
            path_heuristic_code=sys.argv[3]
            
            print(f"[*] Writing the heuristic code from {path_heuristic_code} into gpt.txt...")     
            write_heuristic_on_txt(path_heuristic_code)
            for nb_items,dim in [(250,2),(250,3),(500,2),(500,4),(750,2),(750,3),(750,4)]:
                
                print("[*] Writing the C code into gpt.c...")
                
        
                """write_heuristic(os.path.join(WORK_DIR,"gpt.c"),os.path.join(WORK_DIR,"gpt.c"))"""

                print(f"[*] Compiling WeightACO.c")
                compile(f"WeightACO.c",f"WeightACO_eval_{nb_items}items.exe") 
                run_aco(f"WeightACO_eval_{nb_items}items",args=[f"dataset\\mood_final_val_dataset\\{nb_items}.{dim}.txt"])
            


            print("[*] Extracting Pareto sets from ACO results...")
            dimensions=[2,3,2,4,2,3,4]
            #extraire les sets de pareto à partir des résultats de l'ACO
            for ((algo_result_file, pareto_output_dir), n_dim) in zip(val_aco_results,dimensions):

                extraire_pareto_sets(algo_result_file, pareto_output_dir,n_dim)

            print("[*] Concatenating Pareto sets and filtering with nondominated.exe...")
            #concaténer les sets de pareto extraits pour chaque dataset

            for _,pareto_dir in val_aco_results:
                concatenate_pareto_sets(pareto_dir,3)
            
            print("[*] Calculating  hypervolume and epsilon...")
            #calcul des deux métriques epsilon et hypervolume
            
            
            ##hypervolume
            
            for result_file in val_pareto_set_files:
                print(f"[*]  Hypervolume for dataset {result_file}:")
                mean_hypervolume=calculate_meanHypervolume(val_pareto_set_files)
                print(f"[*]  Hypervolume for dataset {result_file}: {mean_hypervolume}")

            for result_file,ref_pareto_file in zip(val_pareto_set_files,val_pareto_ref_files):
                print(f"[*]  Epsilon for dataset {result_file}:")
                mean_epsilon=calculate_meanEpsilon([result_file],[ref_pareto_file])
                print(f"[*]  Epsilon for dataset {result_file}: {mean_epsilon}")

            
            copy_folder_to_run_dir(
                source_dir=os.path.join(WORK_DIR, "pareto_set_final_val"),
                dest_dir=Path(run_directory)
            )
            

        
        
        finally:
            delete_folder(os.path.join(WORK_DIR, "pareto_set_final_val"))
            for result_file,_ in val_aco_results:
                try: delete_file(result_file)
                except Exception as e:
                    logging.warning(f"Failed to delete {result_file}: {e}")

            
            for nb_items in [250,500,750]:
                try:
                    delete_file(os.path.join(WORK_DIR,f"WeightACO_eval_{nb_items}items.exe"))
                except Exception as e:
                    logging.warning(f"Failed to delete WeightACO_eval_{nb_items}items.exe: {e}")
            
          
    