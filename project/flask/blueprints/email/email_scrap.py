import smtplib, ssl

port = 465
password = 'ayqynfkalncmyska'
context = ssl.create_default_context()


def send_email(message):
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login('rumenplamenov.backend@gmail.com', password)
        server.sendmail('rumenplamenov.backend@gmail.com', 'rumenplamenovart.business@gmail.com', message)
        server.quit()


person = 'Kostadin Krushkov'
subject = f'Message sent from {person}'
message = 'Hi, Rumen nice to meet you. This is my first message.\nRegards, Kostadin'
full_message = f'Subject: {subject}\n\n{message}'
send_email(full_message)