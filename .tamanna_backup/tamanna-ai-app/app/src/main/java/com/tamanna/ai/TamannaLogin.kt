package com.tamanna.ai

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class TamannaLogin : AppCompatActivity() {

    lateinit var username: EditText
    lateinit var password: EditText
    lateinit var loginBtn: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tamanna_login)

        username = findViewById(R.id.username)
        password = findViewById(R.id.password)
        loginBtn = findViewById(R.id.loginBtn)

        loginBtn.setOnClickListener {
            if (username.text.toString() == "admin" &&
                password.text.toString() == "1234") {

                startActivity(Intent(this, TamannaMain::class.java))
                finish()
            } else {
                Toast.makeText(this, "Wrong Login", Toast.LENGTH_SHORT).show()
            }
        }
    }
}