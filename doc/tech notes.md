
### Code files
The foure files main.py, config.py, common.py and command.py constitutes the bare essentials of the system.

main.py loads and starts things
config.py handles configuration data in one big dictionary
common.py makes it all available to all other modules + a few globally useful functions.
command.py handles commands and events throughout the system

All other *.py files in the root, will be loaded if not excluded in the configuration.  

### Start up procedure
* main.py determines the platform PC/ESP32
* Load common.py
* common.py set up the app object and ensure that globals are available
* common.py loads command.py and config.py that loads the configuration from file, if any. (While avoiding circular initialiazion)

The bare basic system is now in place.

* main.py then loads available modules

Each loaded module is the responsible for:
* Setting up default (Factory) configuration setting
* Attaching itself to the app object 
* Registering commands that interact with it, and provide a command handler to call.
* Start its own threads asynchronously as needed

### Commands
Everything is done with commands.
Interaction with any modules function is done with a call to the global cmd function.

usagea: list = cmd(<command string>) 

All commands has the format of **context** **interaction** and **action**
Any of them kan be omittet, if it is meaningful. But the order must be observes.

   Context: is usually the module name. 
   Interaction: is the name of the thing that is to be interacted with, unique within the context
   Action: is what to do with it

If action is omitted it's assumed to be a query of the state og the interaction
If interaction is omitted or is the keyword 'all' it's assumed to mean all interactions in that context

cmd use a rather tolerant interpretation, and will execute if the the first part of the command string makes sense, and ignore the rest

Returns: a list of at least one string.
The first string is either 'ok' or 'failed'
The following strings (if any) is the results og the action or query


