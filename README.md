# TVMaze-Management
### Purpose:
* **Keep track off and manage TV Shows**
	* Using tvmaze.com APIs and standard functionality 
* **Shows:**
	* Track all shows available everywhere in the world (47K+)
		* Automatically "Skip" shows based on rules for 			
			* Language,
			* Network,
			* Runtime,
			* Genres,
			* Types	
		* Decide the Follow or Skip all remaining shows as they are presented automatically in the console
* **Episodes: (For followed shows only)** 
	* Automatically get all episode information 
	* Acquire all episodes for viewing as soon as they are available after their air-date
	* Automatically track episodes as watched or skipped
* **Plex:**
	* Automatically move acquired shows into Plex and notify TVMaze that the show is acquired
* **Technology**
	* Build using Python 3, MariaDB and a little zsh scripting
	* Non Standard Python Libs used:
	    * TVMaze specific created libs:
	        * db_lib
	        * tvm_api.lib
	        * tvm_lib
	        * terminal_lib
        * bs4, re, requests, mariadb, pandas, sqlalchemy, 
        dash, dash_core_components, dash.dependencies, 
        plotly.subplots, plotly.graph.objects
* **Tools**
    * DBeaver - Database Management tool
    * PyCharm - IDE
    * MacOS Catalina (not tested on any other OS)
    * Crontab 
    
## Scheduling of Apps
For scheduling standard crontab is used.  
The following shell scripts are scheduled:

* every 30 minutes a complete run of the apps to interface with TVMaze, Plex and the internet to find and acquire episodes
    * zsh script: tvm_process
* 4 times a day (6am, 9am, 8pm and 10pm the plex cleaned app
    * zsh script: plex_cleanup
These schedule jobs maintain all TVMaze, Plex and TVMaze-Management data.

_Don't forget to include the PYTHONPATH and PATH info in crontab_ 

## Console App
The console app is a terminal based app to manage a lot of different things!

Main Functions are:

* Review New Shows to follow, skip or leave undecided for 7 days
* Manage Shows:
    * Start Following a show
    * Un-follow a show (erase history)
    * Start Skipping episodes for a followed show
    * Change the acquisition provider for a show
* Run Apps directly
    * Run the apps individually
    * Run the whole process
* View all the logs

## View the Statistics
* Start a Dashboard webpage with 15+ graphs

## Screenshots

* Console
  * [Console Menu](https://github.com/dkluis/TVMaze-Management/blob/dev/Docs/Pics/console_shot1.jpg?raw=true)
* Dashboard
  * [Dashboard Top of the page](https://github.com/dkluis/TVMaze-Management/blob/dev/Docs/Pics/dashboard_part1.jpg?raw=true)
  * [Dashboard Bottom of the page](https://github.com/dkluis/TVMaze-Management/blob/dev/Docs/Pics/dashboard_part2.jpg?raw=true)
    
# _Functions & Features:_

### Database
* Detection of the environment (Production or Development) will automatically point access to the right Database
* Console App includes an option to refresh the Development DB with the Production DB data of yesterday
    * Only works if the auto backup is enable in crontab (see crontab example)
* Note:  
DB definition and access is well contained in db_lib.py so changing your implementation to use 
something else than mariaDB will not be hard to accomplish.  SQLite code is commented out but is an example.    

    
