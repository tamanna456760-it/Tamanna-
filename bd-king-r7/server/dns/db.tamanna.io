$TTL 3600
@       IN  SOA     ns1.tamanna.io. admin.tamanna.io. (
                    2025010101  ; Serial
                    7200        ; Refresh
                    3600        ; Retry
                    1209600     ; Expire
                    3600 )      ; Minimum TTL

; Name Servers
@       IN  NS      ns1.tamanna.io.
@       IN  NS      ns2.tamanna.io.

; A Records
@       IN  A       192.0.2.10
www     IN  A       192.0.2.10

; CNAME Records
ftp     IN  CNAME   @

; MX Records (Mail Exchange)
@       IN  MX 10   mail.tamanna.io.
mail    IN  A       192.0.2.20