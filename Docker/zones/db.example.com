$TTL 86400
@   IN  SOA     ns1.example.com. admin.example.com. (
        2024102001 ; Serial
        3600       ; Refresh
        1800       ; Retry
        604800     ; Expire
        86400 )    ; Minimum TTL

    IN  NS  ns1.example.com.
ns1 IN  A   192.168.1.2
www IN  A   192.168.1.3
