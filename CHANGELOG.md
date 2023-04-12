# Changelog

## 0.3.1 (2023-04-12)

#### Fixes

* fix incorrect super().__init() args
#### Refactorings

* use requests.Response built-in json function


## v0.3.0 (2023-04-10)

#### Refactorings

* move push_logs check and call from on_fail decorator to client.send_request()
#### Others

* build v0.3.0
* update changelog


## v0.2.0 (2023-04-03)

#### New Features

* add log_path param to client and logging files to override default behavior
#### Refactorings

* replace pathlib.Path with pathier.Pathier
#### Others

* build v0.2.0
* update changelog
* remove unused imports from client.py


## v0.1.1 (2023-03-22)

#### Others

* build v0.1.1


## v0.1.0 (2023-03-11)

#### New Features

* check for previous server before scanning
* add check to see if previous server is active
* add save_server func
* add func to save config
* add arg to specify config_path
* add load_config function
* add pathlib import to template
#### Fixes

* fix request_model import replacement
#### Performance improvements

* shrink default port range
#### Others

* build v0.1.0
* update changelog
* update test


## v0.0.0 (2023-03-06)

#### New Features

* add arg to generate only certain functions
* add module_to_api script def
* add 'timeout' param to client constructor
* add imports
* automatically detect where to store logs
* add default uvicorn args
* add log_level param to client init
* add basic logging facilities
#### Fixes

* fix failure to import module
* fix text sub in server generator
* fix url path
* fix request_models substitution
* fix app_name default in get_args
* fix app_name default in get_args
* fix directory/destination inconsistency
* fix not creating stream handler w/o reloading module
* fix imports
* fix hardcoded logging level
* change "put" to "post" in client.HomeCloudClient.push_logs()
#### Refactorings

* edit logger exception
* change the way import.util imports
* move _on_fail to module scope as on_fail
* move get_port_range to server.py
* change variable names
* move homecloud and clientlog endpoints to get and post files
* refactor getting ip/port and starting server
#### Others

* build v0.0.0
* add basic documentation
* add requests import
* add return type annotation
* update dependencies
* delete file
* change file extension
* remove unused import
* add file to ignore
* add logging
* delete uneccesary file
* delete uneccessary files
* rename server_logger.py to homecloud_logging.py
* add logs to gitignore