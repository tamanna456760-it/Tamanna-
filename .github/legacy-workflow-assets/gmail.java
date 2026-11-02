public class GmailSender {

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
                                return new PasswordAuthentication("YOUR_GMAIL@gmail.com", "APP_PASSWORD");
                            }
                        });

                Message message = new MimeMessage(session);
                message.setFrom(new InternetAddress("YOUR_GMAIL@gmail.com"));
                message.setRecipients(Message.RecipientType.TO, InternetAddress.parse("YOUR_GMAIL@gmail.com"));
                message.setSubject(subject);
                message.setText(body);

                Transport.send(message);

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }
}
