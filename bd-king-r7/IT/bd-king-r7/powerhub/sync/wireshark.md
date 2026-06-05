
Join Free CTF
Get Kali
Blog
Documentation 
Community 
Courses
Developers 
About 

wireshark
version: 4.6.5 arch: any all
 wireshark Homepage| Package Tracker| Source Code Repository
 Edit this page
Metapackages 
default
everything
large
top10
Tools:
802-11
forensics
respond
sniffing-spoofing
top10
voip
web
wireless
Tool Documentation 
Packages & Binaries 
 libwireshark-data
 libwireshark-dev
 libwireshark19
 libwiretap-dev
 libwiretap16
 libwsutil-dev
 libwsutil17
 stratoshark
strato
stratoshark
 tshark
tshark
 wireshark
wireshark
 wireshark-common
capinfos
captype
dumpcap
editcap
mergecap
mmdbresolve
randpkt
rawshark
reordercap
sharkd
text2pcap
 wireshark-dev
asn2deb
idl2deb
idl2wrs
 wireshark-doc
Learn more with OffSec 
pen-210
LIGHT
DARK
Tool Documentation:
Screenshots
wireshark
wireshark

tshark Usage Example
root@kali:~# tshark -f "tcp port 80" -i eth0
Packages and Binaries:
libwireshark-data
Network packet dissection library – data files
The libwireshark library provides the network packet dissection services developed by the Wireshark project.

This package contains the platform independent files.

Installed size: 3.63 MB
How to install: sudo apt install libwireshark-data

libwireshark-dev
Network packet dissection library – development files
The “libwireshark” library provides the network packet dissection services developed by the Wireshark project.

This package contains the static library and the C header files that are needed for applications to use libwireshark services.

Installed size: 5.10 MB
How to install: sudo apt install libwireshark-dev

Dependencies:
libwireshark19
Network packet dissection library – shared library
The libwireshark library provides the network packet dissection services developed by the Wireshark project.

Installed size: 131.68 MB
How to install: sudo apt install libwireshark19

Dependencies:
libwiretap-dev
Network packet capture library – development files
Wiretap, part of the Wireshark project, is a library that allows one to read and write several packet capture file formats.

Supported formats are:

Libpcap
Sniffer
LANalyzer
Network Monitor
“snoop”
“iptrace”
Sniffer Basic (NetXRay)/Windows Sniffer Pro
RADCOM WAN/LAN Analyzers
Lucent/Ascend access products
HP-UX nettl
Toshiba ISDN Router
ISDN4BSD “i4btrace” utility
Cisco Secure Intrusion Detection System iplogging facility
pppd logs (pppdump-format files)
VMS TCPTRACE
DBS Etherwatch (text format)
Catapult DCT2000 (.out files)
Wiretap’s shortcomings are: no filter capability and no support for packet capture.

This package contains the static library and the C header files.

Installed size: 275 KB
How to install: sudo apt install libwiretap-dev

Dependencies:
libwiretap16
Network packet capture library – shared library
Wiretap, part of the Wireshark project, is a library that allows one to read and write several packet capture file formats.

Supported formats are:

Libpcap
Sniffer
LANalyzer
Network Monitor
“snoop”
“iptrace”
Sniffer Basic (NetXRay)/Windows Sniffer Pro
RADCOM WAN/LAN Analyzers
Lucent/Ascend access products
HP-UX nettl
Toshiba ISDN Router
ISDN4BSD “i4btrace” utility
Cisco Secure Intrusion Detection System iplogging facility
pppd logs (pppdump-format files)
VMS TCPTRACE
DBS Etherwatch (text format)
Catapult DCT2000 (.out files)
Wiretap’s shortcomings are: no filter capability and no support for packet capture.

Installed size: 858 KB
How to install: sudo apt install libwiretap16

Dependencies:
libwsutil-dev
Network packet dissection utilities library – development files
The libwsutil library provides utility functions for Wireshark and related binaries and shared libraries.

This package contains the static library and the C header files that are needed for applications to use the libwsutil library.

Installed size: 546 KB
How to install: sudo apt install libwsutil-dev

Dependencies:
libwsutil17
Network packet dissection utilities library – shared library
The libwsutil library provides utility functions for Wireshark and related binaries and shared libraries.

Installed size: 413 KB
How to install: sudo apt install libwsutil17

Dependencies:
stratoshark
System call and log analyzer - graphical and console interfaces
Stratoshark is a system call and log analyzer. It can capture and analyze system calls on Linux and capture and analyze log data from other sources.

The package provides stratoshark as the graphical interface and strato as the console interface.

Installed size: 16.84 MB
How to install: sudo apt install stratoshark

Dependencies:
strato
Dump and analyze system calls and event logs

root@kali:~# strato -h
strato (Stratoshark) 0.9.5
Dump and analyze network traffic.
See https://www.wireshark.org for more information.

Usage: strato [options] ...

Input file:
  -r <infile>, --read-file <infile>
                           set the filename to read from (or '-' for stdin)

Processing:
  -2                       perform a two-pass analysis
  -M <packet count>        perform session auto reset
  -R <read filter>, --read-filter <read filter>
                           packet Read filter in Wireshark display filter syntax
                           (requires -2)
  -Y <display filter>, --display-filter <display filter>
                           packet displaY filter in Wireshark display filter
                           syntax
  -n                       disable all name resolutions (def: "mNd" enabled, or
                           as set in preferences)
  -N <name resolve flags>  enable specific name resolution(s): "mtndsNvg"
  -d <layer_type>==<selector>,<decode_as_protocol> ...
                           "Decode As", see the man page for details
                           Example: tcp.port==8888,http
  -H <hosts file>          read a list of entries from a hosts file, which will
                           then be written to a capture file. (Implies -W n)
  --enable-protocol <proto_name>
                           enable dissection of proto_name
  --disable-protocol <proto_name>
                           disable dissection of proto_name
  --only-protocols <protocols>
                           Only enable dissection of these protocols, comma
                           separated. Disable everything else
  --disable-all-protocols
                           Disable dissection of all protocols
  --enable-heuristic <short_name>
                           enable dissection of heuristic protocol
  --disable-heuristic <short_name>
                           disable dissection of heuristic protocol
Output:
  -w <outfile|->           write packets to a pcapng-format file named "outfile"
                           (or '-' for stdout). If the output filename has the
                           .gz extension, it will be compressed to a gzip archive
  --capture-comment <comment>
                           add a capture file comment, if supported
  -C <config profile>      start with specified configuration profile
  --global-profile         use the global profile instead of personal profile
  -F <output file type>    set the output file type; default is pcapng.
                           an empty "-F" option will list the file types
  -V                       add output of packet tree        (Packet Details)
  -O <protocols>           Only show packet details of these protocols, comma
                           separated
  -P, --print              print packet summary even when writing to a file
  -S <separator>           the line separator to print between packets
  -x                       add output of hex and ASCII dump (Packet Bytes)
  --hexdump <hexoption>    add hexdump, set options for data source and ASCII dump
     all                   dump all data sources (-x default)
     frames                dump only frame data source
     ascii                 include ASCII dump text (-x default)
     delimit               delimit ASCII dump text with '|' characters
     noascii               exclude ASCII dump text
     time                  include frame timestamp preamble
     notime                do not include frame timestamp preamble (-x default)
     help                  display help for --hexdump and exit
  -T pdml|ps|psml|json|jsonraw|ek|tabs|text|fields|?
                           format of text output (def: text)
  -j <protocolfilter>      protocols layers filter if -T ek|pdml|json selected
                           (e.g. "ip ip.flags text", filter does not expand child
                           nodes, unless child is specified also in the filter)
  -J <protocolfilter>      top level protocol filter if -T ek|pdml|json selected
                           (e.g. "http tcp", filter which expands all child nodes)
  -e <field>               field to print if -Tfields selected (e.g. tcp.port,
                           _ws.col.info)
                           this option can be repeated to print multiple fields
  -E<fieldsoption>=<value> set options for output when -Tfields selected:
     bom=y|n               print a UTF-8 BOM
     header=y|n            switch headers on and off
     separator=/t|/s|<char> select tab, space, printable character as separator
     occurrence=f|l|a      print first, last or all occurrences of each field
     aggregator=,|/s|<char> select comma, space, printable character as
                           aggregator
     quote=d|s|n           select double, single, no quotes for values
  -t (a|ad|adoy|d|dd|e|r|u|ud|udoy)[.[N]]|.[N]
                           output format of time stamps (def: r: rel. to first)
  -u s|hms                 output format of seconds (def: s: seconds)
  -l                       flush standard output after each packet
                           (implies --update-interval 0)
  -q                       be more quiet on stdout (e.g. when using statistics)
  -Q                       only log true errors to stderr (quieter than -q)
  -g                       enable group read access on the output file(s)
  -W n                     Save extra information in the file, if supported.
                           n = write network address resolution information
  -X <key>:<value>         eXtension options, see the man page for details
  -U tap_name              PDUs export mode, see the man page for details
  -z <statistics>          various statistics, see the man page for details
  --export-objects <protocol>,<destdir>
                           save exported objects for a protocol to a directory
                           named "destdir"
  --export-tls-session-keys <keyfile>
                           export TLS Session Keys to a file named "keyfile"
  --color                  color output text similarly to the Wireshark GUI,
                           requires a terminal with 24-bit color support
                           Also supplies color attributes to pdml and psml formats
                           (Note that attributes are nonstandard)
  --no-duplicate-keys      If -T json is specified, merge duplicate keys in an object
                           into a single key with as value a json array containing all
                           values
  --elastic-mapping-filter <protocols> If -G elastic-mapping is specified, put only the
                           specified protocols within the mapping file
  --temp-dir <directory>   write temporary files to this directory
                           (default: /tmp)
  --compress <type>        compress the output file using the type compression format

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -o <name>:<value> ...    override preference setting
  -K <keytab>              keytab file to use for kerberos decryption
  -G [report]              dump one of several available reports and exit
                           default report="fields"
                           use "-G help" for more help

Dumpcap can benefit from an enabled BPF JIT compiler if available.
You might want to enable it by executing:
 "echo 1 > /proc/sys/net/core/bpf_jit_enable"
Note that this can make your system less secure!
stratoshark
System call and event log analyzer

root@kali:~# stratoshark -h
Stratoshark 0.9.5
Interactively dump and analyze system calls and log messages.
See https://www.wireshark.org for more information.

Usage: stratoshark [options] ... [ <infile> ]

Capture source:
  -i <source>, --source <source>
                           name or idx of source (def: first source listed by -D or --list-sources)
  -f <capture filter>      filter in libsinsp/libscap filter syntax
  -y <link type>, --linktype <link type>
                           link layer type (def: first appropriate)
  --time-stamp-type <type> timestamp method for interface
  -D, --list-sources       print list of sources and exit
  -L, --list-data-link-types
                           print list of link-layer types of iface and exit
  --list-time-stamp-types  print list of timestamp types for iface and exit

Capture display:
  -k                       start capturing immediately (def: do nothing)
  -S                       update display when new items are captured
  -l                       turn on automatic scrolling while -S is in use
  --update-interval        interval between updates with new items, in milliseconds (def: 100ms)
Capture stop conditions:
  -c <item count>          stop after n items (def: infinite)
  -a <autostop cond.> ..., --autostop <autostop cond.> ...
                           duration:NUM - stop after NUM seconds
                           filesize:NUM - stop this file after NUM KB
                              files:NUM - stop after NUM files
                             events:NUM - stop after NUM packets
Capture output:
  -b <ringbuffer opt.> ..., --ring-buffer <ringbuffer opt.>
                           duration:NUM - switch to next file after NUM secs
                           filesize:NUM - switch to next file after NUM KB
                              files:NUM - ringbuffer: replace after NUM files
                             events:NUM - switch to next file after NUM events
                           interval:NUM - switch to next file when the time is
                                          an exact multiple of NUM secs
Input file:
  -r <infile>, --read-file <infile>
                           set the filename to read from (no pipes or stdin!)

Processing:
  -R <read filter>, --read-filter <read filter>
                           filter in display filter (wireshark-filter(4)) syntax
  -n                       disable all name resolutions (def: all enabled)
  -N <name resolve flags>  enable specific name resolution(s): "mtndsNvg"
  -d <layer_type>==<selector>,<decode_as_protocol> ...
                           "Decode As", see the man page for details
                           Example: tcp.port==8888,http
  --enable-protocol <proto_name>
                           enable dissection of proto_name
  --disable-protocol <proto_name>
                           disable dissection of proto_name
  --only-protocols <protocols>
                           Only enable dissection of these protocols, comma
                           separated. Disable everything else
  --disable-all-protocols
                           Disable dissection of all protocols
  --enable-heuristic <short_name>
                           enable dissection of heuristic protocol
  --disable-heuristic <short_name>
                           disable dissection of heuristic protocol

User interface:
  -C <config profile>      start with specified configuration profile
  -H                       hide the capture info dialog during capture
  -Y <display filter>, --display-filter <display filter>
                           start with the given display filter
  -g <item number>         go to specified item number after "-r"
  -J <jump filter>         jump to the first item matching the display
                           filter
  -j                       search backwards for a matching item after "-J"
  -t (a|ad|adoy|d|dd|e|r|u|ud|udoy)[.[N]]|.[N]
                           format of time stamps (def: r: rel. to first)
  -u s|hms                 output format of seconds (def: s: seconds)
  -X <key>:<value>         eXtension options, see man page for details
  -z <statistics>          show various statistics, see man page for details

Output:
  -w <outfile|->           set the output filename (or '-' for stdout)
  -F <capture type>        set the output file type; default is pcapng.
                           an empty "-F" option will list the file types.
  --capture-comment <comment>
                           add a capture file comment, if supported
  --temp-dir <directory>   write temporary files to this directory
                           (default: /tmp)

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -P <key>:<path>          persconf:path - personal configuration files
                           persdata:path - personal data files
  -o <name>:<value> ...    override preference or recent setting
  -K <keytab>              keytab file to use for kerberos decryption
  --display <X display>    X display to use
  --fullscreen             start Stratoshark in full screen
tshark
Network traffic analyzer - console version
Wireshark is a network “sniffer” - a tool that captures and analyzes packets off the wire. Wireshark can decode too many protocols to list here.

This package provides the console version of wireshark, named “tshark”.

Installed size: 457 KB
How to install: sudo apt install tshark

Dependencies:
tshark
Dump and analyze network traffic

root@kali:~# tshark -h
TShark (Wireshark) 4.6.5
Dump and analyze network traffic.
See https://www.wireshark.org for more information.

Usage: tshark [options] ...

Capture interface:
  -i <interface>, --interface <interface>
                           name or idx of interface (def: first non-loopback)
  -f <capture filter>      packet filter in libpcap filter syntax
  -s <snaplen>, --snapshot-length <snaplen>
                           packet snapshot length (def: appropriate maximum)
  -p, --no-promiscuous-mode
                           don't capture in promiscuous mode
  -I, --monitor-mode       capture in monitor mode, if available
  -B <buffer size>, --buffer-size <buffer size>
                           size of kernel buffer in MiB (def: 2MiB)
  -y <link type>, --linktype <link type>
                           link layer type (def: first appropriate)
  --time-stamp-type <type> timestamp method for interface
  -D, --list-interfaces    print list of interfaces and exit
  -L, --list-data-link-types
                           print list of link-layer types of iface and exit
  --list-time-stamp-types  print list of timestamp types for iface and exit

Capture display:
  --update-interval        interval between updates with new packets, in milliseconds (def: 100ms)
Capture stop conditions:
  -c <packet count>        stop after n packets (def: infinite)
  -a <autostop cond.> ..., --autostop <autostop cond.> ...
                           duration:NUM - stop after NUM seconds
                           filesize:NUM - stop this file after NUM KB
                              files:NUM - stop after NUM files
                            packets:NUM - stop after NUM packets
Capture output:
  -b <ringbuffer opt.> ..., --ring-buffer <ringbuffer opt.>
                           duration:NUM - switch to next file after NUM secs
                           filesize:NUM - switch to next file after NUM KB
                              files:NUM - ringbuffer: replace after NUM files
                            packets:NUM - switch to next file after NUM packets
                           interval:NUM - switch to next file when the time is
                                          an exact multiple of NUM secs
                         printname:FILE - print filename to FILE when written
                                          (can use 'stdout' or 'stderr')
Input file:
  -r <infile>, --read-file <infile>
                           set the filename to read from (or '-' for stdin)

Processing:
  -2                       perform a two-pass analysis
  -M <packet count>        perform session auto reset
  -R <read filter>, --read-filter <read filter>
                           packet Read filter in Wireshark display filter syntax
                           (requires -2)
  -Y <display filter>, --display-filter <display filter>
                           packet displaY filter in Wireshark display filter
                           syntax
  -n                       disable all name resolutions (def: "mNd" enabled, or
                           as set in preferences)
  -N <name resolve flags>  enable specific name resolution(s): "mtndsNvg"
  -d <layer_type>==<selector>,<decode_as_protocol> ...
                           "Decode As", see the man page for details
                           Example: tcp.port==8888,http
  -H <hosts file>          read a list of entries from a hosts file, which will
                           then be written to a capture file. (Implies -W n)
  --enable-protocol <proto_name>
                           enable dissection of proto_name
  --disable-protocol <proto_name>
                           disable dissection of proto_name
  --only-protocols <protocols>
                           Only enable dissection of these protocols, comma
                           separated. Disable everything else
  --disable-all-protocols
                           Disable dissection of all protocols
  --enable-heuristic <short_name>
                           enable dissection of heuristic protocol
  --disable-heuristic <short_name>
                           disable dissection of heuristic protocol
Output:
  -w <outfile|->           write packets to a pcapng-format file named "outfile"
                           (or '-' for stdout). If the output filename has the
                           .gz extension, it will be compressed to a gzip archive
  --capture-comment <comment>
                           add a capture file comment, if supported
  -C <config profile>      start with specified configuration profile
  --global-profile         use the global profile instead of personal profile
  -F <output file type>    set the output file type; default is pcapng.
                           an empty "-F" option will list the file types
  -V                       add output of packet tree        (Packet Details)
  -O <protocols>           Only show packet details of these protocols, comma
                           separated
  -P, --print              print packet summary even when writing to a file
  -S <separator>           the line separator to print between packets
  -x                       add output of hex and ASCII dump (Packet Bytes)
  --hexdump <hexoption>    add hexdump, set options for data source and ASCII dump
     all                   dump all data sources (-x default)
     frames                dump only frame data source
     ascii                 include ASCII dump text (-x default)
     delimit               delimit ASCII dump text with '|' characters
     noascii               exclude ASCII dump text
     time                  include frame timestamp preamble
     notime                do not include frame timestamp preamble (-x default)
     help                  display help for --hexdump and exit
  -T pdml|ps|psml|json|jsonraw|ek|tabs|text|fields|?
                           format of text output (def: text)
  -j <protocolfilter>      protocols layers filter if -T ek|pdml|json selected
                           (e.g. "ip ip.flags text", filter does not expand child
                           nodes, unless child is specified also in the filter)
  -J <protocolfilter>      top level protocol filter if -T ek|pdml|json selected
                           (e.g. "http tcp", filter which expands all child nodes)
  -e <field>               field to print if -Tfields selected (e.g. tcp.port,
                           _ws.col.info)
                           this option can be repeated to print multiple fields
  -E<fieldsoption>=<value> set options for output when -Tfields selected:
     bom=y|n               print a UTF-8 BOM
     header=y|n            switch headers on and off
     separator=/t|/s|<char> select tab, space, printable character as separator
     occurrence=f|l|a      print first, last or all occurrences of each field
     aggregator=,|/s|<char> select comma, space, printable character as
                           aggregator
     quote=d|s|n           select double, single, no quotes for values
  -t (a|ad|adoy|d|dd|e|r|u|ud|udoy)[.[N]]|.[N]
                           output format of time stamps (def: r: rel. to first)
  -u s|hms                 output format of seconds (def: s: seconds)
  -l                       flush standard output after each packet
                           (implies --update-interval 0)
  -q                       be more quiet on stdout (e.g. when using statistics)
  -Q                       only log true errors to stderr (quieter than -q)
  -g                       enable group read access on the output file(s)
  -W n                     Save extra information in the file, if supported.
                           n = write network address resolution information
  -X <key>:<value>         eXtension options, see the man page for details
  -U tap_name              PDUs export mode, see the man page for details
  -z <statistics>          various statistics, see the man page for details
  --export-objects <protocol>,<destdir>
                           save exported objects for a protocol to a directory
                           named "destdir"
  --export-tls-session-keys <keyfile>
                           export TLS Session Keys to a file named "keyfile"
  --color                  color output text similarly to the Wireshark GUI,
                           requires a terminal with 24-bit color support
                           Also supplies color attributes to pdml and psml formats
                           (Note that attributes are nonstandard)
  --no-duplicate-keys      If -T json is specified, merge duplicate keys in an object
                           into a single key with as value a json array containing all
                           values
  --elastic-mapping-filter <protocols> If -G elastic-mapping is specified, put only the
                           specified protocols within the mapping file
  --temp-dir <directory>   write temporary files to this directory
                           (default: /tmp)
  --compress <type>        compress the output file using the type compression format

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -o <name>:<value> ...    override preference setting
  -K <keytab>              keytab file to use for kerberos decryption
  -G [report]              dump one of several available reports and exit
                           default report="fields"
                           use "-G help" for more help

Dumpcap can benefit from an enabled BPF JIT compiler if available.
You might want to enable it by executing:
 "echo 1 > /proc/sys/net/core/bpf_jit_enable"
Note that this can make your system less secure!
wireshark
Network traffic analyzer - graphical interface
Wireshark is a network “sniffer” - a tool that captures and analyzes packets off the wire. Wireshark can decode too many protocols to list here.

Installed size: 19.12 MB
How to install: sudo apt install wireshark

Dependencies:
wireshark
Interactively dump and analyze network traffic

root@kali:~# wireshark -h
Wireshark 4.6.5
Interactively dump and analyze network traffic.
See https://www.wireshark.org for more information.

Usage: wireshark [options] ... [ <infile> ]

Capture interface:
  -i <interface>, --interface <interface>
                           name or idx of interface (def: first non-loopback)
  -f <capture filter>      packet filter in libpcap filter syntax
  -s <snaplen>, --snapshot-length <snaplen>
                           packet snapshot length (def: appropriate maximum)
  -p, --no-promiscuous-mode
                           don't capture in promiscuous mode
  -I, --monitor-mode       capture in monitor mode, if available
  -B <buffer size>, --buffer-size <buffer size>
                           size of kernel buffer in MiB (def: 2MiB)
  -y <link type>, --linktype <link type>
                           link layer type (def: first appropriate)
  --time-stamp-type <type> timestamp method for interface
  -D, --list-interfaces    print list of interfaces and exit
  -L, --list-data-link-types
                           print list of link-layer types of iface and exit
  --list-time-stamp-types  print list of timestamp types for iface and exit

Capture display:
  -k                       start capturing immediately (def: do nothing)
  -S                       update display when new items are captured
  -l                       turn on automatic scrolling while -S is in use
  --update-interval        interval between updates with new items, in milliseconds (def: 100ms)
Capture stop conditions:
  -c <item count>          stop after n items (def: infinite)
  -a <autostop cond.> ..., --autostop <autostop cond.> ...
                           duration:NUM - stop after NUM seconds
                           filesize:NUM - stop this file after NUM KB
                              files:NUM - stop after NUM files
                            packets:NUM - stop after NUM packets
Capture output:
  -b <ringbuffer opt.> ..., --ring-buffer <ringbuffer opt.>
                           duration:NUM - switch to next file after NUM secs
                           filesize:NUM - switch to next file after NUM KB
                              files:NUM - ringbuffer: replace after NUM files
                            packets:NUM - switch to next file after NUM packets
                           interval:NUM - switch to next file when the time is
                                          an exact multiple of NUM secs
Input file:
  -r <infile>, --read-file <infile>
                           set the filename to read from (no pipes or stdin!)

Processing:
  -R <read filter>, --read-filter <read filter>
                           filter in display filter (wireshark-filter(4)) syntax
  -n                       disable all name resolutions (def: all enabled)
  -N <name resolve flags>  enable specific name resolution(s): "mtndsNvg"
  -d <layer_type>==<selector>,<decode_as_protocol> ...
                           "Decode As", see the man page for details
                           Example: tcp.port==8888,http
  --enable-protocol <proto_name>
                           enable dissection of proto_name
  --disable-protocol <proto_name>
                           disable dissection of proto_name
  --only-protocols <protocols>
                           Only enable dissection of these protocols, comma
                           separated. Disable everything else
  --disable-all-protocols
                           Disable dissection of all protocols
  --enable-heuristic <short_name>
                           enable dissection of heuristic protocol
  --disable-heuristic <short_name>
                           disable dissection of heuristic protocol

User interface:
  -C <config profile>      start with specified configuration profile
  -H                       hide the capture info dialog during capture
  -Y <display filter>, --display-filter <display filter>
                           start with the given display filter
  -g <item number>         go to specified item number after "-r"
  -J <jump filter>         jump to the first item matching the display
                           filter
  -j                       search backwards for a matching item after "-J"
  -t (a|ad|adoy|d|dd|e|r|u|ud|udoy)[.[N]]|.[N]
                           format of time stamps (def: r: rel. to first)
  -u s|hms                 output format of seconds (def: s: seconds)
  -X <key>:<value>         eXtension options, see man page for details
  -z <statistics>          show various statistics, see man page for details

Output:
  -w <outfile|->           set the output filename (or '-' for stdout)
  -F <capture type>        set the output file type; default is pcapng.
                           an empty "-F" option will list the file types.
  --capture-comment <comment>
                           add a capture file comment, if supported
  --temp-dir <directory>   write temporary files to this directory
                           (default: /tmp)

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -P <key>:<path>          persconf:path - personal configuration files
                           persdata:path - personal data files
  -o <name>:<value> ...    override preference or recent setting
  -K <keytab>              keytab file to use for kerberos decryption
  --display <X display>    X display to use
  --fullscreen             start Wireshark in full screen
wireshark-common
Network traffic analyzer - common files
Wireshark is a network “sniffer” - a tool that captures and analyzes packets off the wire. Wireshark can decode too many protocols to list here.

This package provides files common to both wireshark and tshark (the console version).

Installed size: 1.89 MB
How to install: sudo apt install wireshark-common

Dependencies:
capinfos
Prints information about capture files

root@kali:~# capinfos -h
Capinfos (Wireshark) 4.6.5
Print various information (infos) about capture files.
See https://www.wireshark.org for more information.

Usage: capinfos [options] <infile> ...

General infos:
  -t display the capture file type
  -E display the capture file encapsulation
  -I display the capture file interface information
  -F display additional capture file information
  -H display the SHA256 and SHA1 hashes of the file
  -k display the capture comment
  -p display individual packet comments

Size infos:
  -c display the number of packets
  -s display the size of the file (in bytes)
  -d display the total length of all packets (in bytes)
  -l display the packet size limit (snapshot length)

Time infos:
  -u display the capture duration (in seconds)
  -a display the timestamp of the earliest packet
  -e display the timestamp of the latest packet
  -o display the capture file chronological status (True/False)
  -S display earliest and latest packet timestamps as seconds

Statistic infos:
  -y display average data rate (in bytes/sec)
  -i display average data rate (in bits/sec)
  -z display average packet size (in bytes)
  -x display average packet rate (in packets/sec)

Metadata infos:
  -n display number of resolved IPv4 and IPv6 addresses
  -D display number of decryption secrets

Output format:
  -L generate long report (default)
  -T generate table report
  -M display machine-readable values in long reports

Table report options:
  -R generate header record (default)
  -r do not generate header record

  -B separate infos with TAB character (default)
  -m separate infos with comma (,) character
  -b separate infos with SPACE character

  -N do not quote infos (default)
  -q quote infos with single quotes (')
  -Q quote infos with double quotes (")

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -C cancel processing if file open fails (default is to continue)
  -A generate all infos (default)
  -K disable displaying the capture comment
  -P disable displaying individual packet comments

Options are processed from left to right order with later options superseding
or adding to earlier options.

If no options are given the default is to display all infos in long report
output format.
captype
Prints the types of capture files

root@kali:~# captype -h
Captype (Wireshark) 4.6.5
Print the file types of capture files.
See https://www.wireshark.org for more information.

Usage: captype [options] <infile> ...

Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
dumpcap
Dump network traffic

root@kali:~# dumpcap -h
Dumpcap (Wireshark) 4.6.5
Capture network packets and dump them into a pcapng or pcap file.
See https://www.wireshark.org for more information.

Usage: dumpcap [options] ...

Capture interface:
  -i <interface>, --interface <interface>
                           name or idx of interface (def: first non-loopback)
                           or for remote capturing, use this format:
                               TCP@<host>:<port>
  --ifname <name>          name to use in the capture file for a pipe from which
                           we're capturing
  --ifdescr <description>
                           description to use in the capture file for a pipe
                           from which we're capturing
  -f <capture filter>      packet filter in libpcap filter syntax
  -s <snaplen>, --snapshot-length <snaplen>
                           packet snapshot length (def: appropriate maximum)
  -p, --no-promiscuous-mode
                           don't capture in promiscuous mode
  -I, --monitor-mode       capture in monitor mode, if available
  -B <buffer size>, --buffer-size <buffer size>
                           size of kernel buffer in MiB (def: 2MiB)
  -y <link type>, --linktype <link type>
                           link layer type (def: first appropriate)
  --time-stamp-type <type> timestamp method for interface
  -D, --list-interfaces    print list of interfaces and exit
  -L, --list-data-link-types
                           print list of link-layer types of iface and exit
  --list-time-stamp-types  print list of timestamp types for iface and exit
  --update-interval        interval between updates with new packets, in milliseconds (def: 100ms)
  -d                       print generated BPF code for capture filter
  -k <freq>,[<type>],[<center_freq1>],[<center_freq2>]
                           set channel on wifi interface
  -S                       print statistics for each interface once per second
  -M                       for -D, -L, and -S, produce machine-readable output

Stop conditions:
  -c <packet count>        stop after n packets (def: infinite)
  -a <autostop cond.> ..., --autostop <autostop cond.> ...
                           duration:NUM - stop after NUM seconds
                           filesize:NUM - stop this file after NUM kB
                              files:NUM - stop after NUM files
                            packets:NUM - stop after NUM packets
Output (files):
  -w <filename>            name of file to save (def: tempfile)
  -g                       enable group read access on the output file(s)
  -b <ringbuffer opt.> ..., --ring-buffer <ringbuffer opt.>
                           duration:NUM - switch to next file after NUM secs
                           filesize:NUM - switch to next file after NUM kB
                              files:NUM - ringbuffer: replace after NUM files
                            packets:NUM - ringbuffer: replace after NUM packets
                           interval:NUM - switch to next file when the time is
                                          an exact multiple of NUM secs
                          printname:FILE - print filename to FILE when written
                                           (can use 'stdout' or 'stderr')
  -F                       output file type (default: pcapng)
                           an empty "-F" option will list the file types
  -n                       use pcapng format instead of pcap (default)
  -P                       use libpcap format instead of pcapng
  --capture-comment <comment>
                           add a capture comment to the output file
                           (only for pcapng)
  --temp-dir <directory>   write temporary files to this directory
                           (default: /tmp)

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -N <packet_limit>        maximum number of packets buffered within dumpcap
  -C <byte_limit>          maximum number of bytes used for buffering packets
                           within dumpcap
  -t                       use a separate thread per interface
  -q                       don't report packet capture counts
  -Q                       suppress all non-error status messages to stderr
  --application-flavor <flavor>
                           set the application flavor
  -v, --version            print version information and exit
  -h, --help               display this help and exit

Dumpcap can benefit from an enabled BPF JIT compiler if available.
You might want to enable it by executing:
 "echo 1 > /proc/sys/net/core/bpf_jit_enable"
Note that this can make your system less secure!

Example: dumpcap -i eth0 -a duration:60 -w output.pcapng
"Capture packets from interface eth0 until 60s passed into output.pcapng"

Use Ctrl-C to stop capturing at any time.
editcap
Edit and/or translate the format of capture files

root@kali:~# editcap -h
Editcap (Wireshark) 4.6.5
Edit and/or translate the format of capture files.
See https://www.wireshark.org for more information.

Usage: editcap [options] ... <infile> <outfile> [ <packet#>[-<packet#>] ... ]

<infile> and <outfile> must both be present; use '-' for stdin or stdout.
A single packet or a range of packets can be selected.

Packet selection:
  -r                     keep the selected packets; default is to delete them.
  -A <start time>        only read packets whose timestamp is after (or equal
                         to) the given time.
  -B <stop time>         only read packets whose timestamp is before the
                         given time.
                         Time format for -A/-B/-R options is
                         YYYY-MM-DDThh:mm:ss[.nnnnnnnnn][Z|+-hh:mm]
                         Unix epoch timestamps are also supported.

Duplicate packet removal:
  --novlan               remove vlan info from packets before checking for duplicates.
  -d                     remove packet if duplicate (window == 5).
  -D <dup window>        remove packet if duplicate; configurable <dup window>.
                         Valid <dup window> values are 0 to 1000000.
                         NOTE: A <dup window> of 0 with -V (verbose option) is
                         useful to print MD5 hashes.
  -w <dup time window>   remove packet if duplicate packet is found EQUAL TO OR
                         LESS THAN <dup time window> prior to current packet.
                         A <dup time window> is specified in relative seconds
                         (e.g. 0.000001).
           NOTE: The use of the 'Duplicate packet removal' options with
           other editcap options except -V may not always work as expected.
           Specifically the -r, -t or -S options will very likely NOT have the
           desired effect if combined with the -d, -D or -w.
  --skip-radiotap-header skip radiotap header when checking for packet duplicates.
                         Useful when processing packets captured by multiple radios
                         on the same channel in the vicinity of each other.
  --set-unused           set unused byts to zero in sll link addr.

Packet manipulation:
  -s <snaplen>           truncate each packet to max. <snaplen> bytes of data.
  -C [offset:]<choplen>  chop each packet by <choplen> bytes. Positive values
                         chop at the packet beginning, negative values at the
                         packet end. If an optional offset precedes the length,
                         then the bytes chopped will be offset from that value.
                         Positive offsets are from the packet beginning,
                         negative offsets are from the packet end. You can use
                         this option more than once, allowing up to 2 chopping
                         regions within a packet provided that at least 1
                         choplen is positive and at least 1 is negative.
  -L                     adjust the frame (i.e. reported) length when chopping
                         and/or snapping.
  -R <framenum>:<time>   replace the timestamp for given frame number.
                         Accept the same time format as used for -A/-B options.
  -t <time adjustment>   adjust the timestamp of each packet.
                         <time adjustment> is in relative seconds (e.g. -0.5).
  -S <strict adjustment> adjust timestamp of packets if necessary to ensure
                         strict chronological increasing order. The <strict
                         adjustment> is specified in relative seconds with
                         values of 0 or 0.000001 being the most reasonable.
                         A negative adjustment value will modify timestamps so
                         that each packet's delta time is the absolute value
                         of the adjustment specified. A value of -0 will set
                         all packets to the timestamp of the first packet.
  -E <error probability> set the probability (between 0.0 and 1.0 incl.) that
                         a particular packet byte will be randomly changed.
  -o <change offset>     When used in conjunction with -E, skip some bytes from the
                         beginning of the packet. This allows one to preserve some
                         bytes, in order to have some headers untouched.
  --seed <seed>          When used in conjunction with -E, set the seed to use for
                         the pseudo-random number generator. This allows one to
                         repeat a particular sequence of errors.
  -I <bytes to ignore>   ignore the specified number of bytes at the beginning
                         of the frame during MD5 hash calculation, unless the
                         frame is too short, then the full frame is used.
                         Useful to remove duplicated packets taken on
                         several routers (different mac addresses for
                         example).
                         e.g. -I 26 in case of Ether/IP will ignore
                         ether(14) and IP header(20 - 4(src ip) - 4(dst ip)).
  -a <framenum>:<comment> Add or replace packet comment for given frame number.
                         Any pre-existing packet comments from the input file
                         for the specified frame will be replaced unless used
                         in conjunction with "--preserve-packet-comments".
  --discard-packet-comments
                         Discard all pre-existing packet comments from the input
                         file when writing the output file.  Does not discard
                         new comments added by "-a" in the same command line.
  --preserve-packet-comments
                         Preserve from the input file all pre-existing packet
                         comments when adding a new packet comment with "-a".
                         Without this option each "-a" will cause to be
                         discarded any pre-existing comments for the specified
                         frame.

Output File(s):
                         if the output file(s) have the .gz extension, then
                         gzip compression will be used
  -c <packets per file>  split the packet output to different files based on
                         uniform packet counts with a maximum of
                         <packets per file> each.
  -i <seconds per file>  split the packet output to different files based on
                         uniform time intervals with a maximum of
                         <seconds per file> each.
  -F <capture type>      set the output file type; default is pcapng.
                         An empty "-F" option will list the file types.
  -T <encap type>        set the output file encapsulation type; default is the
                         same as the input file. An empty "-T" option will
                         list the encapsulation types.
  --inject-secrets <type>,<file>  Insert decryption secrets from <file>. List
                         supported secret types with "--inject-secrets help".
  --extract-secrets      Extract decryption secrets into the output file instead.
                         Incompatible with other options besides -V.
  --discard-all-secrets  Discard all decryption secrets from the input file
                         when writing the output file.  Does not discard
                         secrets added by "--inject-secrets" in the same
                         command line.
  --capture-comment <comment>
                         Add a capture file comment, if supported.
  --discard-capture-comment
                         Discard capture file comments from the input file
                         when writing the output file.  Does not discard
                         comments added by "--capture-comment" in the same
                         command line.
  --compress <type>      Compress the output file using the type compression format.

Miscellaneous:
  -h, --help             display this help and exit.
  -V                     verbose output.
                         If -V is used with any of the 'Duplicate Packet
                         Removal' options (-d, -D or -w) then Packet lengths
                         and MD5 hashes are printed to standard-error.
  -v, --version          print version information and exit.
mergecap
Merges two or more capture files into one

root@kali:~# mergecap -h
Mergecap (Wireshark) 4.6.5
Merge two or more capture files into one.
See https://www.wireshark.org for more information.

Usage: mergecap [options] -w <outfile>|- <infile> [<infile> ...]

Output:
  -a                concatenate rather than merge files.
                    default is to merge based on frame timestamps.
  -s <snaplen>      truncate packets to <snaplen> bytes of data.
  -w <outfile>|-    set the output filename to <outfile> or '-' for stdout.
                    if the output filename has the .gz extension, it will be compressed to a gzip archive
  -F <capture type> set the output file type; default is pcapng.
                    an empty "-F" option will list the file types.
  -I <IDB merge mode> set the merge mode for Interface Description Blocks; default is 'all'.
                    an empty "-I" option will list the merge modes.
  --compress <type> compress the output file using the type compression format.

Miscellaneous:
  -h, --help        display this help and exit.
  -V                verbose output.
  -v, --version     print version information and exit.
mmdbresolve
Read IPv4 and IPv6 addresses and print their IP geolocation information.

root@kali:~# mmdbresolve -h
mmdbresolve (Wireshark) 4.6.5
Read IPv4 and IPv6 addresses on stdin and print their IP geolocation information on stdout.
See https://www.wireshark.org for more information.

Usage: mmdbresolve [-v|-h] -f <dbfile> [-f <dbfile>] ...

Options:
  -v: display version info and exit
  -h: display this help and exit
  -f: path to a MaxMind Database file

randpkt
Random packet generator

root@kali:~# randpkt -h
Randpkt (Wireshark) 4.6.5
Usage: randpkt [options] <outfile>

Options:
  -b                maximum bytes per packet (default: 5000)
  -c                packet count (default: 1000)
  -F                output file type (default: pcapng)
                    an empty "-F" option will list the file types
  -r                select a different random type for each packet
  -t                packet type
  -h, --help        display this help and exit.
  -v, --version     print version information and exit.

Types:
	arp             Address Resolution Protocol
	bgp             Border Gateway Protocol
	bvlc            BACnet Virtual Link Control
	dns             Domain Name Service
	eth             Ethernet
	fddi            Fiber Distributed Data Interface
	giop            General Inter-ORB Protocol
	icmp            Internet Control Message Protocol
	ieee802.15.4    IEEE 802.15.4
	ip              Internet Protocol
	ipv6            Internet Protocol Version 6
	llc             Logical Link Control
	m2m             WiMAX M2M Encapsulation Protocol
	megaco          MEGACO
	nbns            NetBIOS-over-TCP Name Service
	ncp2222         NetWare Core Protocol
	sctp            Stream Control Transmission Protocol
	syslog          Syslog message
	tds             TDS NetLib
	tcp             Transmission Control Protocol
	tr              Token-Ring
	udp             User Datagram Protocol
	usb-linux       Universal Serial Bus with Linux specific header

If type is not specified, a random packet type will be chosen

rawshark
Dump and analyze raw pcap data

root@kali:~# rawshark -h
Rawshark (Wireshark) 4.6.5
Dump and analyze network traffic.
See https://www.wireshark.org for more information.

Usage: rawshark [options] ...

Input file:
  -r <infile>, --read-file <infile>
                            set the pipe or file name to read from

Processing:
  -d <encap:linktype>|<proto:protoname>
                           packet encapsulation or protocol
  -F <field>               field to display
  -m                       virtual memory limit, in bytes
  -n                       disable all name resolutions (def: "mNd" enabled, or
                           as set in preferences)
  -N <name resolve flags>  enable specific name resolution(s): "mnNtdv"
  -p                       use the system's packet header format
                           (which may have 64-bit timestamps)
  -R <read filter>, --read-filter <read filter>
                           packet filter in Wireshark display filter syntax
  -s                       skip PCAP header on input
  -Y <display filter>, --display-filter <display filter>
                           packet filter in Wireshark display filter syntax
  --enable-protocol <proto_name>
                           enable dissection of proto_name
  --disable-protocol <proto_name>
                           disable dissection of proto_name
  --only-protocols <protocols>
                           Only enable dissection of these protocols, comma
                           separated. Disable everything else
  --disable-all-protocols
                           Disable dissection of all protocols
  --enable-heuristic <short_name>
                           enable dissection of heuristic protocol
  --disable-heuristic <short_name>
                           disable dissection of heuristic protocol

Output:
  -l                       flush output after each packet
  -S                       format string for fields
                           (%D - name, %S - stringval, %N numval)
  -t (a|ad|adoy|d|dd|e|r|u|ud|udoy)[.[N]]|.[N]
                           output format of time stamps (def: r: rel. to first)
  -u s|hms                 output format of seconds (def: s: seconds)

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)


Miscellaneous:
  -h, --help               display this help and exit
  -v, --version            display version info and exit
  -o <name>:<value> ...    override preference setting
  -K <keytab>              keytab file to use for kerberos decryption
reordercap
Reorder input file by timestamp into output file

root@kali:~# reordercap -h
Reordercap (Wireshark) 4.6.5
Reorder timestamps of input file frames into output file.
See https://www.wireshark.org for more information.

Usage: reordercap [options] <infile> <outfile>

Options:
  -n                don't write to output file if the input file is ordered.
  -h, --help        display this help and exit.
  -v, --version     print version information and exit.
sharkd
root@kali:~# sharkd -h
Sharkd (Wireshark) 4.6.5
Daemon variant of Wireshark
See https://www.wireshark.org for more information.

Usage: sharkd [options]
  or   sharkd -

Options:
  -a <socket>, --api <socket>
                           listen on this socket instead of the console
  --foreground             do not detach from console
  -h, --help               show this help information
  -v, --version            show version information
  -C <config profile>, --config-profile <config profile>
                           start with specified configuration profile

Supported socket types:
    unix:/tmp/sharkd.sock - listen on Unix domain socket file /tmp/sharkd.sock
    unix:@sharkd          - listen on abstract Unix socket 'sharkd' (Linux-only)
    (TCP sockets are disabled in this build)

If no socket option is provided, or if 'sharkd -' is used,
sharkd will accept commands via console (standard input).

Examples:
    sharkd -
    sharkd -C myprofile
    sharkd -a unix:/tmp/sharkd.sock -C myprofile

For security reasons, do not directly expose sharkd to the public Internet.
Instead, have a separate backend service to interact with sharkd.

For full details, see https://wiki.wireshark.org/Development/sharkd

text2pcap
Generate a capture file from an ASCII hex dump of packets

root@kali:~# text2pcap -h
Text2pcap (Wireshark) 4.6.5
Generate a capture file from an ASCII hexdump of packets.
See https://www.wireshark.org for more information.

Usage: text2pcap [options] <infile> <outfile>

where  <infile> specifies input  filename (use - for standard input)
      <outfile> specifies output filename (use - for standard output)

Input:
  -o hex|oct|dec|none    parse offsets as (h)ex, (o)ctal, (d)ecimal, or (n)one;
                         default is hex.
  -t <timefmt>           treat the text before the packet as a date/time code;
                         <timefmt> is a format string supported by strptime,
                         with an optional %f descriptor for fractional seconds.
                         Example: The time "10:15:14.5476" has the format code
                         "%H:%M:%S.%f"
                         The special format string ISO supports ISO-8601 times.
                         NOTE: Date/time fields from the current date/time are
                         used as the default for unspecified fields.
  -D                     the text before the packet starts with an I or an O,
                         indicating that the packet is inbound or outbound.
                         This is used when generating dummy headers if the
                         output format supports it (e.g. pcapng).
  -a                     enable ASCII text dump identification.
                         The start of the ASCII text dump can be identified
                         and excluded from the packet data, even if it looks
                         like a HEX dump.
                         NOTE: Do not enable it if the input file does not
                         contain the ASCII text dump.
  -r <regex>             enable regex mode. Scan the input using <regex>, a Perl
                         compatible regular expression matching a single packet.
                         Named capturing subgroups are used to identify fields:
                         <data> (mand.), and <time>, <dir>, and <seqno> (opt.)
                         The time field format is taken from the -t option
                         Example: -r '^(?<dir>[<>])\s(?<time>\d+:\d\d:\d\d.\d+)\s(?<data>[0-9a-fA-F]+)$'
                         could match a file with lines like
                         > 0:00:00.265620 a130368b000000080060
                         < 0:00:00.295459 a2010800000000000000000800000000
  -b 2|8|16|64           encoding base (radix) of the packet data in regex mode
                         (def: 16: hexadecimal) No effect in hexdump mode.

Output:
                         if the output file(s) have the .gz extension, then
                         gzip compression will be used.
  -F <capture type>      set the output file type; default is pcapng.
                         an empty "-F" option will list the file types.
  -E <encap type>        set the output file encapsulation type; default is
                         ether (Ethernet). An empty "-E" option will list
                         the encapsulation types.
  -l <typenum>           set the output file encapsulation type via link-layer
                         type number; default is 1 (Ethernet). See
                         https://www.tcpdump.org/linktypes.html for a list of
                         numbers.
                         Example: -l 7 for ARCNet packets.
  -m <max-packet>        max packet length in output; default is 262144
  -N <intf-name>         assign name to the interface in the pcapng file.
  --compress <type>      Compress the output file using the type compression format.
                         
Prepend dummy header:
  -e <ethertype>         prepend dummy Ethernet II header with specified EtherType
                         (in HEX).
                         Example: -e 0x806 to specify an ARP packet.
  -i <proto>             prepend dummy IP header with specified IP protocol
                         (in DECIMAL).
                         Automatically prepends Ethernet header as well if
                         link-layer type is Ethernet.
                         Example: -i 46
  -4 <srcip>,<destip>    prepend dummy IPv4 header with specified
                         source and destination addresses.
                         Example: -4 10.0.0.1,10.0.0.2
  -6 <srcip>,<destip>    prepend dummy IPv6 header with specified
                         source and destination addresses.
                         Example: -6 2001:db8::b3ff:fe1e:8329,2001:0db8:85a3::8a2e:0370:7334
  -u <srcp>,<destp>      prepend dummy UDP header with specified
                         source and destination ports (in DECIMAL).
                         Automatically prepends Ethernet & IP headers as well.
                         Example: -u 1000,69 to make the packets look like
                         TFTP/UDP packets.
  -T <srcp>,<destp>      prepend dummy TCP header with specified
                         source and destination ports (in DECIMAL).
                         Automatically prepends Ethernet & IP headers as well.
                         Example: -T 50,60
  -s <srcp>,<dstp>,<tag> prepend dummy SCTP header with specified
                         source/destination ports and verification tag (in DECIMAL).
                         Automatically prepends Ethernet & IP headers as well.
                         Example: -s 30,40,34
  -S <srcp>,<dstp>,<ppi> prepend dummy SCTP header with specified
                         source/destination ports and verification tag 0.
                         Automatically prepends a dummy SCTP DATA
                         chunk header with payload protocol identifier ppi.
                         Example: -S 30,40,34
  -P <dissector>         prepend EXPORTED_PDU header with specified dissector
                         as the payload DISSECTOR_NAME tag.
                         Automatically sets link type to Upper PDU Export.
                         EXPORTED_PDU payload defaults to "data" otherwise.

Diagnostic output:
  --log-level <level>      sets the active log level ("critical", "warning", etc.)
  --log-fatal <level>      sets level to abort the program ("critical" or "warning")
  --log-domains <[!]list>  comma-separated list of the active log domains
  --log-fatal-domains <list>
                           list of domains that cause the program to abort
  --log-debug <[!]list>    list of domains with "debug" level
  --log-noisy <[!]list>    list of domains with "noisy" level
  --log-file <path>        file to output messages to (in addition to stderr)

Miscellaneous:
  -h, --help             display this help and exit
  -v, --version          print version information and exit
  -q                     don't report processed packet counts
wireshark-dev
Network traffic analyzer - development tools
Wireshark is a network “sniffer” - a tool that captures and analyzes packets off the wire. Wireshark can decode too many protocols to list here.

This package provides idl2wrs and other files necessary for developing new packet dissectors.

Installed size: 645 KB
How to install: sudo apt install wireshark-dev

Dependencies:
asn2deb
Create a Debian package for BER monitoring from ASN.1

root@kali:~# asn2deb -h
Usage: /usr/bin/asn2deb <parameters>
Parameters are
  --asn      -a asn1file, ASN.1 file to use (mandatory)
  --dbopts   -d opts,     options for dpkg-buildpackage
  --email    -e address,  use e-mail address
  --help     -h,          print help and exit
  --name     -n name,     use user name
  --preserve -p,          do not overwrite files
  --version  -v,          print version and exit
Example:
/usr/bin/asn2deb -e me@foo.net -a bar.asn1 -n "My Name" -d "-rfakeroot -uc -us"
idl2deb
Create a Debian package for CORBA monitoring from IDL

root@kali:~# idl2deb -h
Usage: idl2deb [options]

Example: idl2deb -e me@foo.net -i bar.idl -n "My Name" -d "-rfakeroot -uc -us"

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d opts, --dbopts=opts
                        options for dpkg-buildpackage
  -e address, --email=address
                        use e-mail address
  -i idlfile, --idl=idlfile
                        IDL file to use (mandatory)
  -n name, --name=name  use user name
  -p, --preserve        do not overwrite files
idl2wrs
CORBA IDL to Wireshark Plugin Generator

root@kali:~# man idl2wrs
IDL2WRS(1)                                                           IDL2WRS(1)

NAME
     idl2wrs - CORBA IDL to Wireshark Plugin Generator

SYNOPSIS
     idl2wrs <filename>

DESCRIPTION
     idl2wrs is a program that takes a user specified CORBA IDL file and gener-
     ates "C" source code for a Wireshark "plugin".

     This  resulting  file  can  be compiled as a Wireshark plugin, and used to
     monitor GIOP/IIOP traffic that is using this IDL.

     idl2wrs is actually a shell script wrapper for two Python programs.  These
     programs are:

     *   wireshark_be.py Contains the main IDL Visitor Class

     *   wireshark_gen.py Contains the Source Code Generator Class

     idl2wrs  supports  heuristic dissection of GIOP/IIOP traffic, and some ex-
     perimental code for explicit dissection, based on Object Key  <->  Reposi-
     tory Id mapping. However, code for heuristic based plugins is generated by
     default,  and  users  should consider this the preferred method unless you
     have some namespace collisions.

OPTIONS
     Currently there are no options. idl2wrs can be invoked as follows.

      1. To write the C code to stdout.

             idl2wrs  <your_file.idl>

             eg: idl2wrs echo.idl

      2. To write to a file, just redirect the output.

             idl2wrs echo.idl > packet-test.c

ENVIRONMENT
     idl2wrs will look for wireshark_be.py  and  wireshark_gen.py  in  $PYTHON-
     PATH/site-packages/ and if not found, will try the current directory ./

     The  -p  option  passed  to omniidl (inside idl2wrs) indicates where wire-
     shark_be.py and wireshark_gen.py will be searched. This may need  tweaking
     if you place these files somewhere else.

     If  it complains about being unable to find some modules (eg tempfile.py),
     you may want to check if PYTHONPATH is set correctly.

     eg:  PYTHONPATH=/usr/lib/python3/

SEE ALSO
     wireshark(1), tshark(1)

NOTES
     idl2wrs (including wireshark_be.py and wireshark_gen.py) are part  of  the
     Wireshark  distribution.  The  latest version of Wireshark can be found at
     https://www.wireshark.org.

     idl2wrs uses omniidl, an IDL parser, and can be found at
     http://omniorb.sourceforge.net/

TODO
     Some of the more important things to do are:

     *   Improve Explicit dissection code.

     *   Improve command line options.

     *   Improve decode algorithm when we have operation name collision.

AUTHORS
     Original Author
     Frank Singleton <frank.singleton[AT]ericsson.com>

                                   2026-05-02                        IDL2WRS(1)
wireshark-doc
Network traffic analyzer - documentation
Wireshark is a network “sniffer” - a tool that captures and analyzes packets off the wire. Wireshark can decode too many protocols to list here.

This package contains Wireshark User’s guide, Wireshark Developer’s Guide and the Lua Reference.

Installed size: 13.94 MB
How to install: sudo apt install wireshark-doc



Learn more with OffSec
Want to learn more about wireshark? get access to in-depth training and hands-on labs:

PEN-210: 4. Wireshark Essentials
IT Generalist Common Tools: 1. Wireshark Essentials
MITRE D3FEND - Isolate: 2.2. Introduction to Network Firewalls: Firewall Rules
Digital Forensics Foundations: 6.2.2. Network Forensics: Tcpdump and Wireshark

PEN-210 course



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