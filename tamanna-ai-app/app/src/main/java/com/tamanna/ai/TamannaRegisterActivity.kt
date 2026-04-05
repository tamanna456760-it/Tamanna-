package com.tamanna.ai

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.auth.FirebaseAuth

class TamannaRegisterActivity : AppCompatActivity() {

    lateinit var username: EditText
    lateinit var password: EditText
    lateinit var registerBtn: Button
    private lateinit var auth: FirebaseAuth

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tamanna_register)

        auth = FirebaseAuth.getInstance()

        username = findViewById(R.id.username)
        password = findViewById(R.id.password)
        registerBtn = findViewById(R.id.registerBtn)

        registerBtn.setOnClickListener {
            val email = username.text.toString()
            val pass = password.text.toString()

            auth.createUserWithEmailAndPassword(email, pass)
                .addOnCompleteListener { task ->
                    if (task.isSuccessful) {
                        Toast.makeText(this, "Registration Success", Toast.LENGTH_SHORT).show()
                        startActivity(Intent(this, TamannaLoginActivity::class.java))
                        finish()
                    } else {
                        Toast.makeText(this, "Registration Failed: ${task.exception?.message}", Toast.LENGTH_SHORT).show()
                    }
                }
        }
    }
}