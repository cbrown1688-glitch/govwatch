Starting Container
[2026-04-12 18:45:25 +0000] [1] [INFO] Starting gunicorn 25.3.0
[2026-04-12 18:45:25 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2026-04-12 18:45:25 +0000] [1] [INFO] Using worker: sync
[2026-04-12 18:45:25 +0000] [2] [INFO] Booting worker with pid: 2
[2026-04-12 18:45:25 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl
[2026-04-12 18:45:25 +0000] [2] [ERROR] Exception in worker process
Traceback (most recent call last):
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/arbiter.py", line 713, in spawn_worker
    worker.init_process()
    ~~~~~~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 136, in init_process
    self.load_wsgi()
    ~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 148, in load_wsgi
    self.wsgi = self.app.wsgi()
                ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ~~~~~~~~~~~~~~~~~^^
    return util.import_app(self.app_uri)
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/util.py", line 377, in import_app
    mod = importlib.import_module(module)
  File "/mise/installs/python/3.13.13/lib/python3.13/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1395, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1023, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/app/server.py", line 99, in <module>
    app.run(host='0.0.0.0', port=port)
                                 ^^^^
NameError: name 'port' is not defined
name 'port' is not defined
[2026-04-12 18:45:25 +0000] [1] [ERROR] Worker (pid:2) exited with code 3.
[2026-04-12 18:45:25 +0000] [1] [ERROR] Shutting down: Master
[2026-04-12 18:45:25 +0000] [1] [ERROR] Reason: Worker failed to boot.
[2026-04-12 18:45:25 +0000] [2] [INFO] Worker exiting (pid: 2)
[2026-04-12 18:45:26 +0000] [2] [INFO] Booting worker with pid: 2
[2026-04-12 18:45:26 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl
[2026-04-12 18:45:26 +0000] [1] [INFO] Starting gunicorn 25.3.0
[2026-04-12 18:45:26 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2026-04-12 18:45:26 +0000] [1] [INFO] Using worker: sync
    ~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 148, in load_wsgi
    self.wsgi = self.app.wsgi()
                ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ~~~~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
    return util.import_app(self.app_uri)
[2026-04-12 18:45:26 +0000] [2] [ERROR] Exception in worker process
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
Traceback (most recent call last):
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/util.py", line 377, in import_app
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/arbiter.py", line 713, in spawn_worker
    worker.init_process()
    ~~~~~~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 136, in init_process
    self.load_wsgi()
    mod = importlib.import_module(module)
  File "/mise/installs/python/3.13.13/lib/python3.13/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1395, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1023, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/app/server.py", line 99, in <module>
    app.run(host='0.0.0.0', port=port)
                                 ^^^^
NameError: name 'port' is not defined
name 'port' is not defined
[2026-04-12 18:45:26 +0000] [2] [INFO] Worker exiting (pid: 2)
[2026-04-12 18:45:26 +0000] [1] [ERROR] Worker (pid:2) exited with code 3.
[2026-04-12 18:45:26 +0000] [1] [ERROR] Shutting down: Master
[2026-04-12 18:45:26 +0000] [1] [ERROR] Reason: Worker failed to boot.
[2026-04-12 18:45:27 +0000] [2] [INFO] Booting worker with pid: 2
[2026-04-12 18:45:27 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2026-04-12 18:45:27 +0000] [1] [INFO] Using worker: sync
[2026-04-12 18:45:27 +0000] [1] [INFO] Starting gunicorn 25.3.0
[2026-04-12 18:45:27 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 148, in load_wsgi
    self.wsgi = self.app.wsgi()
                ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ~~~~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
[2026-04-12 18:45:27 +0000] [2] [ERROR] Exception in worker process
    return util.import_app(self.app_uri)
Traceback (most recent call last):
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/arbiter.py", line 713, in spawn_worker
    worker.init_process()
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
    ~~~~~~~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/gunicorn/workers/base.py", line 136, in init_process