import mysql.connector
import imaplib
import email
import html2text

mydb = mysql.connector.connect(host='localhost', user='root', password='vrdella!6', database="alabama")
mycursor = mydb.cursor()  # stores all data from database


def fetch_details(user, password):

    imap_url = 'imap.gmail.com'

    # Connection with GMAIL using SSL
    my_mail = imaplib.IMAP4_SSL(imap_url)

    # Log in using your credentials
    my_mail.login(user, password)

    my_mail.select('Alabama')

    _, data = my_mail.search(None, 'UNSEEN')

    mail_id_list = data[0].split()  # IDs of all emails that we want to fetch

    msgs = []  # empty list to capture all messages
    # Iterate through messages and extract data into the msgs list
    for num in mail_id_list:
        typ, data = my_mail.fetch(num, '(RFC822)')  # RFC822 returns the whole message (BODY fetches just body)
        msgs.append(data)
    return msgs

def client_details(msgs):
    li = []
    html_converter = html2text.HTML2Text()

    for msg in msgs:
        for response_part in msg:
            if type(response_part) is tuple:
                formatted_result = {}
                my_list = []
                my_tuple = tuple()
                my_msg = email.message_from_bytes(response_part[1])

                if "Hold Any" in my_msg['subject']:
                    formatted_result['Status'] = 'On Hold'

                elif "closed" in my_msg['subject']:
                    formatted_result['Status'] = 'Closed'

                if "Requisition #" in my_msg['subject']:
                    value = my_msg['subject'].split("Requisition #")[1].strip('\n')
                    value = value.strip().split("\n")[0].split()[0]
                    formatted_result['Requisition_ID'] = value

                if my_msg.is_multipart():
                    for part in my_msg.walk():
                        # print(part.get_content_type())
                        if part.get_content_type() == 'text/plain':
                            pri = part.get_payload()
                            # print(pri)
                        elif part.get_content_type() == 'text/html':
                            # Convert HTML to plain text using html2text
                            html_content = part.get_payload(decode=True).decode()
                            plain_text = html_converter.handle(html_content)
                            if "The following " in plain_text:
                                value = plain_text.split("The following")[1].strip('\n')
                                value = value.strip().split('.')[0]
                                formatted_result["Comment"] = value

                            print(formatted_result)
                            for i in formatted_result:
                                my_list.append(formatted_result[i])
                            my_tuple = tuple(my_list)
                            li.append(my_tuple)
    print(li)
    stmt = "INSERT INTO state_of_alabama_details (Status, Requisition_ID,Comment) VALUES (%s, %s, %s)"
    mycursor.executemany(stmt, li)
    print('data inserted')


mail = fetch_details(user='pooja@vrdella.com', password='fqsp cnki xzas tnsq')

client_details(mail)

mydb.commit()
mydb.close()
print("Data Inserted Successfully")



