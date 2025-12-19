# ipcmm
Configuration management and monitoring tool

 ![alt text](https://github.com/samkrao/ipcmm/blob/main/architecture.png?raw=true)
	
* Purpose:
Provide configure management and monitoring system which is light weight and highly scalable , performant.
* What problem we are trying to solve
  Currently most of the configuration management tools are console base
     * Providing nice UI to operate
     * Performance monitoring with customizable by integration to any performance monitoring tool a
     * Security monitoring with customizatble by integration to any security testing tool
     * Network monitoring with customizable by intigration to any network monitoring tool
* Other features:
	- On Demand push configuration in sync mode (connection is held till configuration is in progress)
	- On Demand pull configuration management where agent is forced to apply latest configurations if any from configuration servers
	- Reactor base configuration management. This will be part of push configuration but in async mode where the first configuration is pushed to agent and disconnected on the result returned by agent the workflow / orchestration of other configurations happens in similar fashion
	- Nodes are not tied to any particular master or servers
* Security:
	- Any communication between servers or servers and agents will be through two way ssl and with symmetric key encryption
	- Also between servers and agents the authentication is using service keys (including vault server) which will be changed at every stipulated time period like token based authentication

## 📜 Licensing Model

Ipcmm uses a **[LGPL V3](https://www.gnu.org/licenses/lgpl-3.0.en.html)**:
