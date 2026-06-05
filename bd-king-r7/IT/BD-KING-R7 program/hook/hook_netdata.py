import psutil

def network_stats():
    net = psutil.net_io_counters()

    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv
    }

if __name__ == "__main__":
    print(network_stats())