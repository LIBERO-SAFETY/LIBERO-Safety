exp_name=pi0_libero_plus_vanilla
exp_name=pi05_libero_plus_vanilla
exp_name=pi05_libero_plus_exps
task_name=${1}
port=${2}
resume_id=${3}
python main.py --args.task_suite_name=${task_name} --args.exp_name=${exp_name} --args.port=${port} --args.resume_id=${resume_id} 