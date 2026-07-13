package com.tamanna.tiai

import android.os.Bundle
import android.widget.EditText
import android.widget.ImageButton
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {
    private lateinit var chatAdapter: ChatAdapter
    private val messages = mutableListOf<ChatMessage>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        val inputMsg = findViewById<EditText>(R.id.inputMsg)
        val sendBtn = findViewById<ImageButton>(R.id.sendBtn)

        chatAdapter = ChatAdapter(messages)
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = chatAdapter

        sendBtn.setOnClickListener {
            val userText = inputMsg.text.toString().trim()
            if (userText.isNotEmpty()) {
                addMessage(ChatMessage(userText, true))
                inputMsg.text.clear()
                val botReply = TIBot.getReply(userText)  // TI Bot ব্যবহার
                addMessage(ChatMessage(botReply, false))
            }
        }
        addMessage(ChatMessage("👋 Hello! I'm TI AI. Ask me anything.", false))
    }

    private fun addMessage(msg: ChatMessage) {
        messages.add(msg)
        chatAdapter.notifyItemInserted(messages.size - 1)
        findViewById<RecyclerView>(R.id.recyclerView).scrollToPosition(messages.size - 1)
    }
}