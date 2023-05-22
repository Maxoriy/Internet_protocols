import socket
from base64 import b64encode
from ssl import wrap_socket
from configparser import ConfigParser

parser = ConfigParser(allow_no_value=True)

with open('config.cfg', encoding="utf-8") as file:
    parser.read_file(file)

message = parser['Message']
boundary = message['Boundary']
account = parser['Account']

with open(message['Text'], encoding="utf-8") as file:
    text = file.read()

if text[0] == '.':
    text = '.' + text

attachments = ''
for attachment in message['Attachments'].split('\n')[1:]:
    filename, mime_type = attachment.split(',')
    with open(filename.strip(), 'rb') as f:
        file = b64encode(f.read())
        attachments += (
                           f'Content-Disposition: attachment; filename="{filename.strip()}"\n'
                           'Content-Transfer-Encoding: base64\n'
                           f'Content-Type: {mime_type.strip()}; name="{filename.strip()}"\n\n'
                       ) + file.decode() + f'\n--{boundary}'

login = account['Login']
recipients = ','.join(parser['Recipients'])
subject = f'=?utf-8?B?{b64encode(message["Subject"].encode()).decode()}?='

prepare_message = (
    f'From: {login}\n'
    f'To: {recipients}\n'
    f'Subject: {subject}\n'
    'MIME-Version: 1.0\n'
    f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n'
    f'--{boundary}\n'
    'Content-Type: text/plain; charset=utf-8\n'
    'Content-Transfer-Encoding: 8bit\n\n'
    f'{text}\n'
    f'--{boundary}\n'
    f'{attachments}--\n.'
)


def execute_command(s, cmd):
    s.send(cmd + b'\n')
    return s.recv(1024).decode()


login = login.encode()
password = account['Password'].encode()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock = wrap_socket(sock)
    server = parser['Server']
    sock.connect((server['Address'], int(server['Port'])))
    print(execute_command(sock, b'EHLO script'))
    print(execute_command(sock, b'AUTH LOGIN'))
    print(execute_command(sock, b64encode(login)))
    print(execute_command(sock, b64encode(password)))
    print(execute_command(sock, b'MAIL FROM: ' + login))
    for recipient in parser['Recipients']:
        print(execute_command(sock, b'RCPT TO: ' + recipient.encode()))
    print(execute_command(sock, b'DATA'))
    print(execute_command(sock, prepare_message.encode()))
    print('Message sent')
