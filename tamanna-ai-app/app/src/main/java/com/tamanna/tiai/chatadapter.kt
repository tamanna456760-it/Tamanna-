package com.tamanna.tiai

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ChatAdapter(private val messages: MutableList<ChatMessage>) :
    RecyclerView.Adapter<ChatAdapter.ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.message_item, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val msg = messages[position]
        holder.textView.text = msg.text
        if (msg.isUser) {
            holder.textView.setBackgroundResource(R.drawable.user_bubble)
        } else {
            holder.textView.setBackgroundResource(R.drawable.bot_bubble)
        }
    }

    override fun getItemCount() = messages.size

    class ViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView = itemView.findViewById(R.id.tvMessage)
    }
}

data class ChatMessage(val text: String, val isUser: Boolean)