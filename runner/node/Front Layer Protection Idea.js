setInterval(() => {
    fetch("/heartbeat")
        .catch(() => {
            console.log("Server unstable - switching backup node");
        });
}, 5000);