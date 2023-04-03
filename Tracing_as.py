import os
from json import loads
from urllib.request import urlopen
from argparse import ArgumentParser

PRIVATE_IP_ADDRESS = [
    ('10.0.0.0', '10.255.255.255'),
    ('172.16.0.0', '172.31.255.255'),
    ('192.168.0.0', '192.168.255.255'),
    ('127.0.0.0', '127.255.255.255')
]

CONST = 0


def get_full_info(ip: str) -> str:
    global CONST
    information = loads(urlopen(f"https://ipinfo.io/{ip}/json").read())
    try:
        org = information['org'].split(maxsplit=1)
        CONST += 1
        return f"{CONST} | {ip} | {org[0]} | {org[-1]} | " \
               f"{information['country']} | {information['city']} |" \
               f" {information['region']}"
    except KeyError:
        CONST += 1
        return f"{CONST} | {ip} | *** | *** | {information['country']} | " \
               f"{information['city']} | {information['region']}"


def tracing_as(destination: str, hops: int) -> str:
    os.system(f"tracert -h {hops} {destination} > tracing_path.txt")
    with open("tracing_path.txt", 'r') as file:
        lst_data = map(lambda x: x.split(), file.readlines()[3:])
        lst_ip = map(clean_ip,
                     [value[-1] for value in [row for row in lst_data if row] if
                      value[-1] != '.'])
        for ip in lst_ip:
            if is_public(ip):
                yield get_full_info(ip)


def clean_ip(ip: str) -> str:
    if '[' in ip:
        return ip[1:-1]
    return ip


def is_public(ip: str) -> bool:
    for private_ip in PRIVATE_IP_ADDRESS:
        if private_ip[0] <= ip <= private_ip[1]:
            return False
    return True


def main():
    parser = ArgumentParser(description="Tracing of autonomous system")
    parser.add_argument('destination', type=str, help='Destination')
    parser.add_argument('-hops', type=int, default=30,
                        help='Maximum number of hops')
    args = parser.parse_args()
    print("№ | IP | AS | PROVIDER | COUNTRY | CITY | REGION")
    for row in tracing_as(args.destination, args.hops):
        print(row)


if __name__ == '__main__':
    main()
