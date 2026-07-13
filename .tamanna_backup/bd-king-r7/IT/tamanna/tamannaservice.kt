class TamannaService : Service() {
  override fun onCreate() {
    super.onCreate()
    startForeground(1, NotificationHelper.build(this, "Tamanna Active"))
    // initialize engines, schedule periodic syncs
  }

  override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    // start background tasks: file saver, heartbeat monitor, docker sync triggers via server
    return START_STICKY
  }

  override fun onBind(intent: Intent?) = null
}
