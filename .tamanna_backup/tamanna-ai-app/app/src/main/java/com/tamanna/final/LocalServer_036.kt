package com.tamanna.final

import java.net.ServerSocket

class LocalServer_036 {

    fun startServer(port: Int = 8080) {
        Thread {
            val server = ServerSocket(port)
            while (true) {
                val client = server.accept()
                val output = client.getOutputStream()
                output.write("AI Server Running".toByteArray())
                output.flush()
                client.close()
            }
        }.start()
    }
}