
Join Free CTF
Get Kali
Blog
Documentation 
Community 
Courses
Developers 
About 

metasploit-framework
version: 6.4.133 arch: any
 metasploit-framework Homepage| Package Tracker| Source Code Repository
 Edit this page
Metapackages 
default
everything
large
top10
Tools:
exploitation
identify
information-gathering
post-exploitation
reverse-engineering
social-engineering
top10
vulnerability
web
Tool Documentation 
Packages & Binaries 
 metasploit-framework
msf-egghunter
msf-exe2vba
msf-exe2vbs
msf-find_badchars
msf-halflm_second
msf-hmac_sha1_crack
msf-java_deserializer
msf-jsobfu
msf-makeiplist
msf-md5_lookup
msf-metasm_shell
msf-msf_irb_shell
msf-nasm_shell
msf-pattern_create
msf-pattern_offset
msf-pdf2xdp
msf-virustotal
msfconsole
msfd
msfdb
msfrpc
msfrpcd
msfupdate
msfvenom
Learn more with OffSec 
pen-200
LIGHT
DARK
Tool Documentation:
Video

msfrpcd
root@kali:~# msfrpcd -h

Usage: msfrpcd <options>

OPTIONS:

    -P <opt>  Specify the password to access msfrpcd
    -S        Disable SSL on the RPC socket
    -U <opt>  Specify the username to access msfrpcd
    -a <opt>  Bind to this IP address
    -f        Run the daemon in the foreground
    -h        Help banner
    -n        Disable database
    -p <opt>  Bind to this port instead of 55553
    -t <opt>  Token Timeout (default 300 seconds
    -u <opt>  URI for Web server
Metasploit-Framework Usage Examples
One of the best sources of information on using the Metasploit Framework is Metasploit Unleashed, a free online course created by OffSec. Metasploit Unleashed guides you from the absolute basics of Metasploit all the way through to advanced topics.

Packages and Binaries:
metasploit-framework
Framework for exploit development and vulnerability research
The Metasploit Framework is an open source platform that supports vulnerability research, exploit development, and the creation of custom security tools.

Installed size: 564.96 MB
How to install: sudo apt install metasploit-framework

Dependencies:
msf-egghunter
root@kali:~# msf-egghunter -h
Usage: msf-egghunter [options]
Example: msf-egghunter -f python -e W00T

Specific options:
    -f, --format <String>            See --list-formats for a list of supported output formats
    -b, --badchars <String>          (Optional) Bad characters to avoid for the egg
    -e, --egg <String>               The egg (Please give 4 bytes)
    -p, --platform <String>          (Optional) Platform
        --startreg <String>          (Optional) The starting register
        --forward                    (Optional) To search forward
        --depreg <String>            (Optional) The DEP register
        --depdest <String>           (Optional) The DEP destination
        --depsize <Integer>          (Optional) The DEP size
        --depmethod <String>         (Optional) The DEP method to use (virtualprotect/virtualalloc/copy/copy_size)
    -a, --arch <String>              (Optional) Architecture
        --list-formats               List all supported output formats
    -v, --var-name <name>            (Optional) Specify a custom variable name to use for certain output formats
    -h, --help                       Show this message
msf-exe2vba
root@kali:~# msf-exe2vba -h
    Usage: msf-exe2vba [exe] [vba]
msf-exe2vbs
root@kali:~# msf-exe2vbs -h
    Usage: msf-exe2vbs [exe] [vbs]
msf-find_badchars
root@kali:~# msf-find_badchars -h

    Usage: msf-find_badchars <options>

OPTIONS:

    -b   The list of characters to avoid: '\x00\xff'
    -h   Help banner
    -i   Read memory contents from the supplied file path
    -t   The format that the memory contents are in (empty to list)
msf-halflm_second
root@kali:~# msf-halflm_second -h

    Usage: msf-halflm_second <options>

OPTIONS:

    -h   Display this help information
    -n   The encrypted LM hash to crack
    -p   The decrypted LANMAN password for bytes 1-7
    -s   The server challenge (default value 1122334455667788)
msf-hmac_sha1_crack
root@kali:~# msf-hmac_sha1_crack -h

Usage: msf-hmac_sha1_crack hashes.txt <wordlist | - >
The format of hash file is <identifier>:<hex-salt>:<hash>

msf-java_deserializer
root@kali:~# msf-java_deserializer -h
Usage: msf-java_deserializer <file> [option]
    -a, --array=ID                   Print detailed information about content array
    -o, --object=ID                  Print detailed information about content object
    -h, --help                       Prints this help
msf-jsobfu
root@kali:~# msf-jsobfu -h
Usage: msf-jsobfu [options]

Specific options:
    -t, --iteration <Integer>        Number of times to obfuscate the JavaScript
    -i, --input <String>             The JavaScript file you want to obfuscate (default=1)
    -o, --output <String>            Save the obfuscated file as
    -p id1,id2,                      The identifiers to preserve
        --preserved-identifiers
    -h, --help                       Show this message
msf-makeiplist
msf-md5_lookup
root@kali:~# msf-md5_lookup -h
Usage: msf-md5_lookup [options]

Specific options:
    -i, --input <file>               The file that contains all the MD5 hashes (one line per hash)
    -d, --databases <names>          (Optional) Select databases: all, authsecu, i337, md5_my_addr, md5_net, md5crack, md5cracker, md5decryption, md5online, md5pass, netmd5crack, tmto (Default=all)
    -o, --out <filepath>             (Optional) Save the results to a file (Default=md5_results.txt)
    -h, --help                       Show this message
msf-metasm_shell
root@kali:~# msf-metasm_shell -h

Usage: msf-metasm_shell <options>

OPTIONS:

    -a   The architecture to encode as (ARM, Ia32, MIPS, X86_64)
    -e   The endianness to encode as (big, little)
    -h   Display this help information
msf-msf_irb_shell
root@kali:~# msf-msf_irb_shell -h
Usage:  irb.rb [options] [programfile] [arguments]
  -f                Don't initialize from configuration file.
  -d                Set $DEBUG and $VERBOSE to true (same as 'ruby -d').
  -r load-module    Require load-module (same as 'ruby -r').
  -I path           Specify $LOAD_PATH directory (same as 'ruby -I').
  -U                Set external and internal encodings to UTF-8.
  -E ex[:in]        Set default external (ex) and internal (in) encodings
                    (same as 'ruby -E').
  -w                Enable warnings (same as 'ruby -w' or 'ruby -W1').
  -W[level=2]       Set warning level: 0=silence, 1=medium, 2=verbose
                    (same as 'ruby -W').
  --context-mode n  Set n[0-5] to method to create Binding Object,
                    when new workspace was created.
  --extra-doc-dir   Add an extra doc dir for the doc dialog.
  --echo            Show result (default).
  --noecho          Don't show result.
  --echo-on-assignment
                    Show result on assignment.
  --noecho-on-assignment
                    Don't show result on assignment.
  --truncate-echo-on-assignment
                    Show truncated result on assignment (default).
  --inspect         Use 'inspect' for output.
  --noinspect       Don't use 'inspect' for output.
  --no-pager        Don't use pager.
  --multiline       Use multiline editor module (default).
  --nomultiline     Don't use multiline editor module.
  --singleline      Use single line editor module.
  --nosingleline    Don't use single line editor module (default).
  --colorize        Use color-highlighting (default).
  --nocolorize      Don't use color-highlighting.
  --autocomplete    Use auto-completion (default).
  --noautocomplete  Don't use auto-completion.
  --regexp-completor
                    Use regexp based completion (default).
  --type-completor  Use type based completion.
  --prompt prompt-mode, --prompt-mode prompt-mode
                    Set prompt mode. Pre-defined prompt modes are:
                    'default', 'classic', 'simple', 'inf-ruby', 'xmp', 'null'.
  --inf-ruby-mode   Use prompt appropriate for inf-ruby-mode on emacs.
                    Suppresses --multiline and --singleline.
  --sample-book-mode, --simple-prompt
                    Set prompt mode to 'simple'.
  --noprompt        Don't output prompt.
  --script          Script mode (default, treat first argument as script)
  --noscript        No script mode (leave arguments in argv)
  --single-irb      Share self with sub-irb.
  --tracer          Show stack trace for each command.
  --back-trace-limit n[=16]
                    Display backtrace top n and bottom n.
  --verbose         Show details.
  --noverbose       Don't show details.
  -v, --version     Print the version of irb.
  -h, --help        Print help.
  --                Separate options of irb from the list of command-line args.
msf-nasm_shell
root@kali:~# msf-nasm_shell -h
0 bits not supported
msf-pattern_create
root@kali:~# msf-pattern_create -h
Usage: msf-pattern_create [options]
Example: msf-pattern_create -l 50 -s ABC,def,123
Ad1Ad2Ad3Ae1Ae2Ae3Af1Af2Af3Bd1Bd2Bd3Be1Be2Be3Bf1Bf

Options:
    -l, --length <length>            The length of the pattern
    -s, --sets <ABC,def,123>         Custom Pattern Sets
    -h, --help                       Show this message
msf-pattern_offset
root@kali:~# msf-pattern_offset -h
Usage: msf-pattern_offset [options]
Example: msf-pattern_offset -q Aa3A
[*] Exact match at offset 9

Options:
    -q, --query Aa0A                 Query to Locate
    -l, --length <length>            The length of the pattern
    -s, --sets <ABC,def,123>         Custom Pattern Sets
    -h, --help                       Show this message
msf-pdf2xdp
root@kali:~# msf-pdf2xdp -h
    Usage: msf-pdf2xdp input.pdf output.xdp
msf-virustotal
root@kali:~# msf-virustotal -h
Usage: msf-virustotal [options]

Specific options:
    -k <key>                         (Optional) Virusl API key to use
    -d <seconds>                     (Optional) Number of seconds to wait for the report
    -q                               (Optional) Do a hash search without uploading the sample
    -f <filenames>                   Files to scan

Common options:
    -h, --help                       Show this message
msfconsole
Metasploit Framework Console

root@kali:~# msfconsole -h
Usage: msfconsole [options]

Common options:
    -E, --environment ENVIRONMENT    Set Rails environment, defaults to RAIL_ENV environment variable or 'production'

Database options:
    -M, --migration-path DIRECTORY   Specify a directory containing additional DB migrations
    -n, --no-database                Disable database support
    -y, --yaml PATH                  Specify a YAML file containing database settings

Framework options:
    -c FILE                          Load the specified configuration file
    -v, -V, --version                Show version

Module options:
        --[no-]defer-module-loads    Defer module loading unless explicitly asked
    -m, --module-path DIRECTORY      Load an additional module path

Console options:
    -a, --ask                        Ask before exiting Metasploit or accept 'exit -y'
    -H, --history-file FILE          Save command history to the specified file
    -l, --logger STRING              Specify a logger to use (StdoutWithoutTimestamps, TimestampColorlessFlatfile, Flatfile, Stderr, Stdout)
        --[no-]readline
    -L, --real-readline              Use the system Readline library instead of RbReadline
    -o, --output FILE                Output to the specified file
    -p, --plugin PLUGIN              Load a plugin on startup
    -q, --quiet                      Do not print the banner on startup
    -r, --resource FILE              Execute the specified resource file (- for stdin)
    -x, --execute-command COMMAND    Execute the specified console commands (use ; for multiples)
    -h, --help                       Show this message
msfd
root@kali:~# msfd -h

Usage: msfd <options>

OPTIONS:

    -a   Bind to this IP address instead of loopback
    -A   Specify list of hosts allowed to connect
    -D   Specify list of hosts not allowed to connect
    -f   Run the daemon in the foreground
    -h   Help banner
    -p   Bind to this port instead of 55554
    -q   Do not print the banner on startup
    -s   Use SSL
msfdb
root@kali:~# msfdb -h

Manage the metasploit framework database

You can use an specific port number for the
PostgreSQL connection setting the PGPORT variable
in the current shell.

Example: PGPORT=5433 msfdb init

  msfdb init     # start and initialize the database
  msfdb reinit   # delete and reinitialize the database
  msfdb delete   # delete database and stop using it
  msfdb start    # start the database
  msfdb stop     # stop the database
  msfdb status   # check service status
  msfdb run      # start the database and run msfconsole

msfrpc
root@kali:~# msfrpc -h

Usage: msfrpc <options>

OPTIONS:

    -a   Connect to this IP address
    -h   Help banner
    -p   Connect to the specified port instead of 55553
    -P   Specify the password to access msfrpcd
    -S   Disable SSL on the RPC socket
    -U   Specify the username to access msfrpcd
msfrpcd
root@kali:~# msfrpcd -h

Usage: msfrpcd <options>

OPTIONS:

    -a   Bind to this IP address (default: 0.0.0.0)
    -c   (JSON-RPC) Path to certificate (default: /root/.msf4/msf-ws-cert.pem)
    -f   Run the daemon in the foreground
    -h   Help banner
    -j   (JSON-RPC) Start JSON-RPC server
    -k   (JSON-RPC) Path to private key (default: /root/.msf4/msf-ws-key.pem)
    -n   Disable database
    -p   Bind to this port (default: 55553)
    -P   Specify the password to access msfrpcd
    -S   Disable SSL on the RPC socket
    -t   Token Timeout seconds (default: 300)
    -U   Specify the username to access msfrpcd
    -u   URI for Web server
    -v   (JSON-RPC) SSL enable verify (optional) client cert requests
msfupdate
root@kali:~# msfupdate -h
msfupdate is no longer supported when Metasploit is part of the operating
system. Please use 'apt update; apt install metasploit-framework'
msfvenom
Payload Generator and Encoder

root@kali:~# msfvenom -h
MsfVenom - a Metasploit standalone payload generator.
Also a replacement for msfpayload and msfencode.
Usage: /usr/bin/msfvenom [options] <var=val>
Example: /usr/bin/msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> -f exe -o payload.exe

Options:
    -l, --list            <type>     List all modules for [type]. Types are: payloads, encoders, nops, platforms, archs, encrypt, formats, all
    -p, --payload         <payload>  Payload to use (--list payloads to list, --list-options for arguments). Specify '-' or STDIN for custom
        --list-options               List --payload <value>'s standard, advanced and evasion options
    -f, --format          <format>   Output format (use --list formats to list)
    -e, --encoder         <encoder>  The encoder to use (use --list encoders to list)
        --service-name    <value>    The service name to use when generating a service binary
        --sec-name        <value>    The new section name to use when generating large Windows binaries. Default: random 4-character alpha string
        --smallest                   Generate the smallest possible payload using all available encoders
        --encrypt         <value>    The type of encryption or encoding to apply to the shellcode (use --list encrypt to list)
        --encrypt-key     <value>    A key to be used for --encrypt
        --encrypt-iv      <value>    An initialization vector for --encrypt
    -a, --arch            <arch>     The architecture to use for --payload and --encoders (use --list archs to list)
        --platform        <platform> The platform for --payload (use --list platforms to list)
    -o, --out             <path>     Save the payload to a file
    -b, --bad-chars       <list>     Characters to avoid example: '\x00\xff'
    -n, --nopsled         <length>   Prepend a nopsled of [length] size on to the payload
        --pad-nops                   Use nopsled size specified by -n <length> as the total payload size, auto-prepending a nopsled of quantity (nops minus payload length)
    -s, --space           <length>   The maximum size of the resulting payload
        --encoder-space   <length>   The maximum size of the encoded payload (defaults to the -s value)
    -i, --iterations      <count>    The number of times to encode the payload
    -c, --add-code        <path>     Specify an additional win32 shellcode file to include
    -x, --template        <path>     Specify a custom executable file to use as a template
    -k, --keep                       Preserve the --template behaviour and inject the payload as a new thread
    -v, --var-name        <value>    Specify a custom variable name to use for certain output formats
    -t, --timeout         <second>   The number of seconds to wait when reading the payload from STDIN (default 30, 0 to disable)
        --refresh-cache              Rebuild the module metadata cache from disk before listing
    -h, --help                       Show this message


Learn more with OffSec
Want to learn more about metasploit-framework? get access to in-depth training and hands-on labs:

PEN-200: 21. The Metasploit Framework

PEN-200 course



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