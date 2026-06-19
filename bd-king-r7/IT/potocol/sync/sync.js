class SyncSystem {
    constructor() {
        this.status = "online";
        this.lastSync = new Date();
    }

    sync() {
        this.lastSync = new Date();
        console.log(`Sync completed at ${this.lastSync}`);
    }

    ping(host) {
        console.log(`Checking connection to ${host}`);
    }
}

const sync = new SyncSystem();
sync.sync();
sync.ping("localhost");