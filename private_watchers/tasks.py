from celery import shared_task
from django.utils.timezone import now  # type: ignore
import colorama, json, requests, time, subprocess, pydig, os
from requests.exceptions import RequestException
from .models import *


def send_message(message: str, telegram: bool = False, colour: str = "YELLOW", logger: bool = True):
    color = getattr(colorama.Fore, colour.upper(), colorama.Fore.YELLOW)
    print(color + message + colorama.Style.RESET_ALL)

    timestamp = time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime())
    if logger:
        with open('logger.txt', 'a', encoding='utf-8') as file:
            file.write(f"{message} -> {timestamp}\n")

    if telegram:
        escaped_message = message.replace(' ', '+')
        command = (
            f'curl -X POST "https://api.telegram.org/bot6348870305:AAHawStCiN6XfiAu_ZwQJU-x8C1XtKjZ2XA/sendMessage" '
            f'-d "chat_id=5028701156&text={escaped_message}"'
        )
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_subfinder(domain):
    try:
        send_message(f"[info] Starting Subfinder for '{domain}'...", telegram=True)
        output = os.popen(f"subfinder -d {domain} -silent -timeout 20 -max-time 20").read()
        subdomains = [line.strip() for line in output.splitlines() if line.strip()]
        send_message(f"[info] {len(subdomains)} subs found for {domain}", colour='GREEN')
        return subdomains
    except Exception as e:
        send_message(f"Error running Subfinder on {domain}: {e}", colour='RED')
        return []


def process_subfinder(domains):
    try:
        tool = Tool.objects.get(tool_name='subfinder')
        for domain in domains:
            wildcards = WatchedWildcard.objects.filter(is_active=True, tools__tool_name='subfinder', wildcard=domain)

            wildcards.update(status='running')
            subdomains = run_subfinder(domain)

            for wildcard in wildcards:
                wildcard.status = 'running'
                wildcard.save()
                clear_labels(wildcard)
                for sub in subdomains:
                    obj, created = DiscoverSubdomain.objects.update_or_create(
                        wildcard=wildcard, subdomain=sub, defaults={'tool': tool}
                    )
                    if created:
                        obj.label = "new"
                        obj.save()
                wildcard.status = 'completed'
                wildcard.save()
    except Exception as e:
        send_message(f"Process Subfinder error: {e}", colour='RED')


def clear_labels(watcher):
    DiscoverSubdomain.objects.filter(wildcard=watcher).update(label="available")


def check_a_record(domain: str) -> bool:
    try:
        fake_domain = f"nonexistent1234.{domain}"
        result = pydig.query(fake_domain, 'A')
        if result:
            send_message(f"[info] A record verification failed for {domain}", colour='RED')


            return False
        send_message(f"[info] A record check passed for {domain}", colour='GREEN')
        return True
    except Exception as e:
        send_message(f"DNS A record check error: {e}", colour='RED')
        return False


def process_dns_bruteforce(watcher_assets):
    dns_tool = Tool.objects.get(tool_name='dns_bruteforce')

    for asset in watcher_assets:
        for wildcard in asset.wildcards.all():
            if not wildcard.tools.filter(tool_name='dns_bruteforce').exists():
                continue

            if not check_a_record(wildcard.wildcard):
                wildcard.status = 'failed'
                wildcard.save()
                continue

            send_message(f"[info] Starting DNSBruteforce for {wildcard.wildcard}", telegram=True)
            subdomains = generate_dns_wordlist(asset, wildcard)

            # First Shuffledns
            shuffle_out = f"private_watchers/outputs/shuffle_out.txt"
            cmd = (
                f"shuffledns -d {wildcard.wildcard} -w private_watchers/wordlists/{asset.user.username}/dnsbruteforce_all.txt "
                f"-r private_watchers/outputs/resolvers.txt -o {shuffle_out} -silent"
            )
            os.popen(cmd).read()

            # DNSGen
            dnsgen_in = f"private_watchers/outputs/dnsgen_subs.txt"
            dnsgen_out = f"private_watchers/outputs/dnsgen_out.txt"
            combine_dnsgen_input(shuffle_out, asset, wildcard, dnsgen_in)
            os.popen(f"dnsgen {dnsgen_in} | tee {dnsgen_out}").read()

            # Second Shuffledns
            os.popen(
                f"shuffledns -d {wildcard.wildcard} -w {dnsgen_out} -r private_watchers/outputs/resolvers.txt -o private_watchers/outputs/dns_gen_shuffle_out.txt -silent"
            ).read()

            # Save results
            save_discovered_subs([shuffle_out, dnsgen_out], wildcard, dns_tool)
            wildcard.status = 'completed'
            wildcard.save()
            send_message(f"[done] DNSBrute completed for {asset}", colour='GREEN')


def generate_dns_wordlist(asset, wildcard):
    discovered_file = f"private_watchers/wordlists/{asset.user.username}/dnsbruteforce_discovered.txt"
    combined_file = f"private_watchers/wordlists/{asset.user.username}/dnsbruteforce_all.txt"

    subfinder_subs = run_subfinder(wildcard.wildcard)
    clean_subs = [s.replace(f".{wildcard.wildcard}", '') for s in subfinder_subs if s]

    with open(discovered_file, 'w') as f:
        f.writelines([f"{s}\n" for s in clean_subs])

    with open(asset.dns_bruteforce_wordlist.path, 'r') as f:
        static_words = [line.strip() for line in f if line.strip()]

    combined = set(clean_subs + static_words)
    with open(combined_file, 'w') as f:
        f.writelines([f"{word}\n" for word in combined])

    send_message(f"[info] {len(combined)} subdomains collected for DNS bruteforce", colour='GREEN')
    return combined


def combine_dnsgen_input(shuffle_result_path, asset, wildcard, output_file):
    with open(shuffle_result_path, 'r') as f:
        shuffle_subs = [line.strip().replace(f".{wildcard.wildcard}", '') for line in f if line.strip()]

    discovered_file = f"private_watchers/wordlists/{asset.user.username}/dnsbruteforce_discovered.txt"
    with open(discovered_file, 'r') as f:
        discovered_subs = [line.strip() for line in f if line.strip()]

    combined = set(shuffle_subs + discovered_subs)
    with open(output_file, 'w') as f:
        f.writelines([f"{sub}\n" for sub in combined])


def save_discovered_subs(paths, wildcard, tool):
    subs = set()
    for path in paths:
        with open(path, 'r') as f:
            subs.update(line.strip() for line in f if line.strip())

    for sub in subs:
        obj, created = DiscoverSubdomain.objects.update_or_create(
            wildcard=wildcard, subdomain=sub, defaults={'tool': tool}
        )
        if created:
            obj.label = "new"
            obj.save()


@shared_task
def check_assets():
    assets = AssetWatcher.objects.filter(is_active=True)
    AssetWatcher.objects.filter(is_active=True).update(status='pending')

    subfinder_domains = set()
    for asset in assets:
        try:
            for wildcard in asset.wildcards.all():
                wildcard.status = 'pending'
                wildcard.save()

                for tool in wildcard.tools.all():
                    if tool.tool_name == 'subfinder':
                        subfinder_domains.add(wildcard.wildcard)

        except Exception as e:
            asset.status = 'failed'
            asset.save()
            send_message(f"[error] Failed to process {asset}: {e}", colour='RED')

    try:
        pass
        # process_subfinder(subfinder_domains)
        # process_dns_bruteforce(assets)
        
    except Exception as e:
        send_message(f"[error] Subdomain discovery failed: {e}", colour='RED')

    AssetWatcher.objects.filter(is_active=True).update(status='completed')