
Join Free CTF
Get Kali
Blog
Documentation 
Community 
Courses
Developers 
About 

powershell-empire
version: 6.5.0 arch: all
 powershell-empire Homepage| Package Tracker| Source Code Repository
 Edit this page
Metapackages 
default
everything
large
Packages & Binaries 
 powershell-empire
powershell-empire
starkiller
starkiller-start
starkiller-stop
Learn more with OffSec 
LIGHT
DARK
Packages and Binaries:
powershell-empire
PowerShell and Python post-exploitation agent
This package contains a post-exploitation framework that includes a pure-PowerShell2.0 Windows agent, and a pure Python Linux/OS X agent. It is the merge of the previous PowerShell Empire and Python EmPyre projects. The framework offers cryptologically-secure communications and a flexible architecture. On the PowerShell side, Empire implements the ability to run PowerShell agents without needing powershell.exe, rapidly deployable post-exploitation modules ranging from key loggers to Mimikatz, and adaptable communications to evade network detection, all wrapped up in a usability-focused framework.

Installed size: 49.87 MB
How to install: sudo apt install powershell-empire

Dependencies:
powershell-empire
root@kali:~# powershell-empire -h
usage: empire.py [-h] {server,setup} ...

positional arguments:
  {server,setup}
    server        Launch Empire Server
    setup         Setup the data directories for Empire

options:
  -h, --help      show this help message and exit
starkiller
root@kali:~# starkiller -h
┏━(Message from Kali developers)
┃
┃ The command starkiller is deprecated. Please use starkiller-start instead.
┃
┗━
starkiller-start
root@kali:~# starkiller-start -h

┏━(Message from Kali developers)
┃ 
┃ Service status:
┃   * powershell-empire.service - Powershell-Empire service
┃        Loaded: loaded (/usr/lib/systemd/system/powershell-empire.service; 5:185mdisabled; preset: 5:185mdisabled)
┃        Active: active (running) since Thu 2026-05-28 06:16:39 EDT; 2s ago
┃    Invocation: ae82a2a07c64424982edf654d46f5b0a
┃      Main PID: 22230 (python3)
┃         Tasks: 65:245m (limit: 6535)
┃        Memory: 129.3M (peak: 129.4M)
┃           CPU: 1.345s
┃        CGroup: /system.slice/powershell-empire.service
┃                `-5:245m22230 python3 empire.py server
┃   
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Starkiller enabled. Loading. 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Starkiller served at the same ip and port as Empire Server 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Starkiller served at http://localhost:1337/ 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Started server process [22230] 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Waiting for application startup. 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Application startup complete. 
┃   May 28 06:16:40 kali powershell-empire[22230]: [INFO]: Uvicorn running on http://0.0.0.0:1337 (Press CTRL+C to quit) 
┃   May 28 06:16:41 kali powershell-empire[22230]: [WARNING]: Invalid HTTP request received. 
┃   May 28 06:16:41 kali powershell-empire[22230]: [INFO]: 127.0.0.1:52132 - "GET / HTTP/1.1" 200 
┃   May 28 06:16:41 kali powershell-empire[22230]: [INFO]: Shutting down 
┃ 
┃  Default credentials:
┃    user: empireadmin
┃    password: password123
┃ 
┗━

starkiller-stop
root@kali:~# starkiller-stop -h

┏━(Message from Kali developers)
┃ 
┃ Service status:
┃   * powershell-empire.service - Powershell-Empire service
┃        Loaded: loaded (/usr/lib/systemd/system/powershell-empire.service; 5:185mdisabled; preset: 5:185mdisabled)
┃        Active: inactive (dead)
┃   
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Waiting for application shutdown. 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Empire shutting down... 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Shutting down listeners... 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Shutting down plugins... 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Shutting down SocketIO... 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Application shutdown complete. 
┃   May 28 06:16:43 kali powershell-empire[22356]: [INFO]: Finished server process [22356] 
┃   May 28 06:16:43 kali systemd[1]: powershell-empire.service: Deactivated successfully.
┃   May 28 06:16:43 kali systemd[1]: Stopped powershell-empire.service - Powershell-Empire service.
┃   May 28 06:16:43 kali systemd[1]: powershell-empire.service: Consumed 1.348s CPU time over 2.224s wall clock time, 129.3M memory peak.
┃ 
┗━



Learn more with OffSec
Want to learn more about powershell-empire? get access to in-depth training and hands-on labs:

Rule Creation and Refinement Skill Path: 3.3.1. Network Detections: C2 Infrastructure
MITRE D3FEND - Detect: 9.3.1. Network Detections: C2 Infrastructure
MITRE ATT&CK - Detect: 4.3.1. Network Detections: C2 Infrastructure
PowerShell Empire


Updated on: 2026-May-25

Edit this page
LIGHT
DARK
Links
Home
Download / Get Kali
Blog
OS Documentation
Tool Documentation
System Status
Archived Releases
Partnerships
Platforms
ARM (SBC)
NetHunter (Mobile)

 Amazon AWS
 Docker
 Linode
 Microsoft Azure
 Microsoft Store (WSL)
 Vagrant
Development
Bug Tracker
Continuous Integration
Network Mirror
Package Tracker
 GitLab
Community
 Discord
Support Forum

 PeerTube
Follow Us
 Bluesky
 Facebook
 Instagram
 Mastodon
 Substack
 X

 Newsletter
 RSS
Policies
Cookie Policy
Privacy Policy
Trademark Policy
© OffSec Services Limited 2026. All rights reserved.
Kali Linux is part of OffSec's Community Projects
Learn more about OffSec's free, open-source penetration testing tools for cybersecurity professionals