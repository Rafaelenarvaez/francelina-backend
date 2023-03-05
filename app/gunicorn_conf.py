from multiprocessing import cpu_count

# Socket Path

bind = 'unix:/home/ubuntu/projects/francelina-backend/app/gunicorn.sock'

# Worker Options

workers = cpu_count() + 1

worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options

loglevel = 'debug' 

accesslog = '/home/ubuntu/projects/francelina-backend/access_log'

errorlog =  '/home/ubuntu/projects/francelina-backend/error_log'
