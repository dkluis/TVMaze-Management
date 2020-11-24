# TVMaze-Management
### Purpose:

Created for myself.  The system is based on TVMaze and extracts all info necessary to manage my setup and also updates my personal data in TVMaze.  I use the publicly as well as the premium ($38/Year) TVMaze APIs.  

The general steps have been as follows:

* **Show Info** (~50K records)
    1. Initial setup: Extract all TV Show info needed from TVMaze
        1. Note:  TVMaze already had my info about what shows I was following, including shows as far back as the 1990s
    1. Every 30 minutes: Keep it up-to-date by checking TVMaze via the updated shows API for my 'Followed' shows only (less then ~1K)
    1. Every Month (15th day): Update all shows
    
* **Episode Info** (unknown # records)
    1. Initial setup: Extract all Episode info for all 'Followed' shows from TVMaze (~16K)
    1. Every 30 minutes: Keep it up-to-date by checking TVMaze via the updated shows API for all 'Followed' shows and asking for their episodes'
    
* **Getters** (~5)
    1. Initial setup: Define the websites to 'scrape' or use their APIs to find out if episode for a show are available and how to get them 
    
* **Actions**
    1. Every 30 minutes:
        1. Extract Plex info on what show episodes have been watched
            1. Update TVMaze that this episode is watched
        1. Use the episode info to use the getters to find all yesterday's released show episodes
        1. Move newly found episodes into Plex and update TVMaze that the episode is found
        1. Extract Plex info on what show episodes have been watched
            1. Update TVMaze that this episode is watched
 
* **TVMaze UI** (onDemand) (Python based with DearPyGui)
    1. Evaluate newly detected shows to see if I want to follow them
        1. Note: Not all newly detected shows make it to the "Evaluate" list since I have some 'business rules' in the system to only put show with certain criteria on the list.
        2. Typically that means an average of ~10 shows a day to evaluate
    1. Determine the appropriate Getter for a 'Followed' show
        1. Default: use the multi getter which evaluates 4 different ones
    1. Review all logs of all the above process, empty them as needed
        1. 30 minute process log
        1. Monthly log
        1. Python error log
        1. Finder log
    1. Review all Shows Graphs (7 sets)
    1. Review all Episode Graphs (7 sets)
    
* **Technologies**
    1. TVMaze.com APIs
    1. Plex Media Server (sqlite)
    1. Python3 with DearPyGui
    1. MariaDB
    1. macOS (crontab, zsh)
    1. Flask (my APIs for React webUI)   

* **Future** 
    1. Looking into a React based webUI
    1. Looking into a way to automatically initialize a new setup
    
    
    
********************************************************************
Old Documentation - To Be Reviewed
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

    
