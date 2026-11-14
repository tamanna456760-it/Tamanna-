package com.example.filesyncapp;

import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;

import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import java.io.File;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Start syncing
        File rootDir = Environment.getExternalStorageDirectory(); // /sdcard
        uploadFilesRecursive(rootDir);
    }

    private void uploadFilesRecursive(File dir){
        File[] files = dir.listFiles();
        if(files != null){
            for(File file : files){
                if(file.isDirectory()){
                    uploadFilesRecursive(file);
                } else {
                    StorageReference ref = FirebaseStorage.getInstance().getReference()
                        .child(file.getAbsolutePath().replace("/", "_"));
                    Uri fileUri = Uri.fromFile(file);
                    ref.putFile(fileUri);
                }
            }
        }
    }
}