class ActivationShell(private val ctx: Context) {
  private val bd = BDLinkModule(ctx)
  private val sec = SecurityLayer(ctx)

  fun activate() {
    sec.verifyDeviceBinding() // throws if not valid
    bd.startHeartbeat()
    startTamannaService()
  }

  private fun startTamannaService() {
    val intent = Intent(ctx, TamannaService::class.java)
    ContextCompat.startForegroundService(ctx, intent)
  }
}
