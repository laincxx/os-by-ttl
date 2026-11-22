import ipaddress
import platform
import re
import subprocess
import sys


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def get_os_by_ip(ip_address: str) -> str:
    current_os = platform.system().lower()
    param = '-n' if current_os == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        output = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
        )
    except subprocess.CalledProcessError:
        return f'Узел {ip_address} недоступен или не отвечает на ICMP-запросы.'
    except subprocess.TimeoutExpired:
        return 'Ping не завершился за отведённое время.'
    except FileNotFoundError:
        return 'Команда ping не найдена в системе.'

    match = re.search(r'ttl[=:]\s*(\d+)', output, re.IGNORECASE)
    if not match:
        return 'Не удалось найти TTL в ответе (возможно, узел блокирует ping).'

    ttl = int(match.group(1))

    if ttl <= 64:
        os_guess = 'Linux / Unix / macOS'
    elif ttl <= 128:
        os_guess = 'Windows'
    elif ttl <= 255:
        os_guess = 'Сетевое оборудование (Cisco и т.п.) / Solaris'
    else:
        os_guess = 'Неизвестная ОС'

    return (f'IP: {ip_address} | TTL: {ttl} | '
            f'Вероятная ОС (эвристика): {os_guess}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_ip = sys.argv[1].strip()
    else:
        target_ip = input('Введите IP-адрес для проверки: ').strip()

    if not target_ip:
        print('IP-адрес не введён.')
        sys.exit(1)

    if not is_valid_ip(target_ip):
        print(f'«{target_ip}» не похож на корректный IP-адрес.')
        sys.exit(1)

    print(get_os_by_ip(target_ip))
