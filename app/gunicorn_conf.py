from multiprocessing import cpu_count

# Socket Path

bind = 'unix:/home/ubuntu/proyects/francelina-backend/app/gunicorn.sock'

# Worker Options

workers = cpu_count() + 1

worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options

loglevel = 'debug' 

accesslog = '/home/ubuntu/proyects/francelina-backend/access_log'

errorlog =  '/home/ubuntu/proyects/francelina-backend/error_log'
