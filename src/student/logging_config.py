import logging 
import os 

def logging_service():
    log_dir ='logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "student_vm_service.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
