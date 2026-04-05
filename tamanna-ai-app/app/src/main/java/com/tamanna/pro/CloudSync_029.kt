package com.tamanna.pro

import com.google.firebase.firestore.FirebaseFirestore

class CloudSync_029 {

    private val db = FirebaseFirestore.getInstance()

    fun uploadData(collection: String, data: Map<String, Any>) {
        db.collection(collection).add(data)
    }

    fun fetchData(collection: String, callback: (List<Map<String, Any>>) -> Unit) {
        db.collection(collection).get().addOnSuccessListener { result ->
            val list = result.map { it.data }
            callback(list)
        }
    }
}