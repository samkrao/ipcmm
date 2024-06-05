# ipcmm
Configuration management and monitoring tool
Why Python
Scripting
* Fast development
* Available on almost all kinds of oses only installation needed is for windos
* Multi threading  byThread and threading
* Async by asyncio
* Multi processing by multiprocessing
* Concurrent by concurrent	
* Event driven
* eventlet
* Twisted
* Tornado
* Reactor
* Twisted
* Reactor
* Fibers
* Fibers
* Greenlet
* Coroutines/generator
* Yield keyword/method
* Easy system calls to run system commands
* Sys, os, shutils etc
* Pointers ????
- Pointers.py pip

 ![alt text](https://github.com/samkrao/ipcmm/blob/main/architecture.png?raw=true)
	
* Purpose:
Provide configure management and monitoring system which is light weight and highly scalable , performant.
* Other features:
	- On Demand push configuration in sync mode (connection is held till configuration is in progress)
	- On Demand pull configuration management where agent is forced to apply latest configurations if any from configuration servers
	- Reactor base configuration management. This will be part of push configuration but in async mode where the first configuration is pushed to agent and disconnected on the result returned by agent the workflow / orchestration of other configurations happens in similar fashion
	- Nodes are not tied to any particular master or servers
* Security:
	- Any communication between servers or servers and agents will be through two way ssl and with symmetric key encryption
	- Also between servers and agents the authentication is using service keys (including vault server) which will be changed at every stipulated time period like token based authentication

* Components 
	- Master Servers
		- Infra Provision
		- Configuration on Agentless clients
		- clusters (HA/Load balancing)/shards/federation/shovels
	- Reactor Servers
		+ In agent base when configuring though Master in async mode
		+ Capture job /configuration status or events to process next event
		- Clusters (active/passive or primary and secondary)
	- Alerting/Reporting proxies
		+ Gather data regarding 
		+ CPU
		+ Memory
		+ System Health
		- Configuration/job status
		- Process and forward to Alert/monitoring server
		- Alert/message to different messaging systems
		- Clusters
  	- Alert And Monitoring Server
		+ Store the information supplied by proxies to Database
		+ Multi Master and slaves
	- Config Server
		+ Parse the configuration information for syntax and Semantics and cache in sequence of commands
  		+ Master slave replication or ring kind with raft or paxos with shards/federation/shovels
	- Monitoring and Client Agents
		+ Retrieve configurations to be applied for the given node 
		+ Send system health data to event bus queues in regular intervals
		+ Send configuration status to evenbus queue
		+ Clusters
	- DB
		+ Hold the configuration information
		+ Job/configuration status for each node
		+ Health check data of each node for further processing
	- Event Bus Queues
	  	+ Asynchronous data handling
* Configuration languages
	- YAML (Initial Release)
	- JSON
	- XML
	- Property files
		+ Pre compiled and parsed for syntax and semantics upfront to pyc or any other native code rather than loading yamls/properties
		+ Any modifications to existing should be applied using diff (like virtual dom/incremental dom) means only modifications should be parsed and processed, not whole config file
		+I t should be one time activity by config servers



* Syntax and semantics 
	- declare:
		+ in:
		+ out:
		+ inout:
		+ ref:
		+ ptr:
		+ addr:
	
	- define:
		+ func:
		+ proc:
		+ lambda:
	
	\<Label\>:\
  	  &nbsp; &nbsp; &nbsp; \<build in functions\>:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- target:\
	     &thinsp; &thinsp; &emsp; &emsp; &emsp; \- env:\
	     &thinsp; &thinsp; &emsp; &emsp; &emsp;  \- args:\
	     &thinsp; &thinsp; &nbsp; &ensp; &emsp; &emsp; &emsp;\- 1\
	     &thinsp;&thinsp; &nbsp; &ensp; &emsp; &emsp; &emsp; \- 2\
	     &thinsp; &thinsp; &emsp; &emsp; &emsp; \- depends_on:\
	     &thinsp; &thinsp; &emsp; &emsp; &emsp; \- requires/requires_any/requires_none:\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;\- 1\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;\- 2\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- stoponfail: True | False\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- modeofexec: [parallel |  concurrent | queue | sync | async | seq ]\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- params:\
 	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- context:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- result:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- order:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runafter:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runbefore:\
             &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runaround:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- onfail:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- onsuccess:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- onchange:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runonsuccess:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runonfail:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- watch:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- listen:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- prereq:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- postreq:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- use:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- onlyif:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- when:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- loop_if:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- loop_until:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- loop_in:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- test:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- runas:\
	     &thinsp; &thinsp; &ensp; &ensp; &ensp; &ensp;\- retry:\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;attempts: 3\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;interval: 10\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;until: True\
	     &thinsp; &thinsp; &nbsp;&nbsp;&nbsp; &ensp; &emsp; &emsp; &emsp;splay: 60\
	     \&nbsp; 
	\#build in functions\
	\#ipcmm.run.cmd\
	\#ipcmm.run.script\
	\#ipcmm.include\
	\#ipcmm.import\
	\#ipcmm.call\
	\#ipcmm.invoke\
	\#ipcmm.exec\
	\#ipcmm.spawn\
	\#ipcmm.eval\
	\#ipcmm.apply\
	\#ipcmm.event\
	\#ipcmm.fire\
	\#ipcmm.bind\
	\#ipcmm.unbind\
	\#ipcmm.os\
	\#ipcmm.sys\
	\#ipcmm.vm\
	\#ipcmm.container\
	\#ipcmm.unik\
	\#ipcmm.hypervisor\
	\#ipcmm.crypto\
	\#ipcmm.network\
	\#ipcmm.filesystem\
  	\#ipcmm.memory\
  	\#ipcmm.cpu\
  	\#ipcmm.nop\
  	\#ipcmm.sleep\
  	\#ipcmm.wait\
  	\#ipcmm.parallel\
  	\#ipcmm.concurrent\
  	\#ipcmm.async\
  	\#ipcmm.schedule\
  	\#ipcmm.dynamic\
  	\#ipcmm.static\
  	\#ipcmm.fork\
  	\#ipcmm.join\
  	\#ipcmm.react\
  	\#ipcmm.ssh\
  	\#ipcmm.winrm\
  	\#ipcmm.winrs\
  	\#ipcmm.psremoting\
  	\#ipcmm.psexec\
  	\#ipcmm.scp\
  	\#ipcmm.agents\
  	\#ipcmm.servers\
  	\#ipcmm.masters\
	\#ipcmm.slaves\
	\#ipcmm.nodes

