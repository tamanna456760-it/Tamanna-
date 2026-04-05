package com.tamanna.git.api.token

import android.content.Context
import java.io.File

/**
 * TokenManager_081
 * 
 * Purpose:
 * - Store token securely in app's local folder: api/token
 * - Retrieve token safely for automation / sync
 */
class TokenManager_081(private val context: Context) {

    private val tokenFolder = File(context.filesDir, "api/token")
    private val tokenFileName = "token.txt"

    init {
        if (!tokenFolder.exists()) {
            tokenFolder.mkdirs() // create api/token folder if not exists
        }
    }

    /**
     * Save token securely
     */
    fun saveToken(token: String) {
        val file = File(tokenFolder, tokenFileName)
        file.writeText(token)
        println("✅ Token saved at ${file.absolutePath}")
    }

    /**
     * Read token safely
     */
    fun getToken(): String? {
        val file = File(tokenFolder, tokenFileName)
        return if (file.exists()) file.readText() else null
    }

    /**
     * Sync token to another location (optional backup)
     */
    fun syncTokenTo(remotePath: String) {
        val token = getToken()
        if (token != null) {
            val remoteFile = File(remotePath, tokenFileName)
            remoteFile.writeText(token)
            println("🔄 Token synced to $remotePath")
        } else {
            println("❌ No token found to sync")
        }
    }
}