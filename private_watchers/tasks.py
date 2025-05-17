from celery import shared_task
from django.utils.timezone import now  # type: ignore
import colorama, json, requests, time, subprocess, pydig, os
from requests.exceptions import RequestException
from .models import *
from datetime import datetime


OUTPUT_PATH = 'private_watchers/outputs'
WORDLISTS_PATH = 'private_watchers/wordlists'


def sendmessage(message: str, telegram: bool = False, colour: str = "YELLOW", logger: bool = True):
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
        sendmessage(f"[info] Starting Subfinder for '{domain}'...", telegram=False)
        output = os.popen(f"subfinder -d {domain} -all -silent -timeout 60 -max-time 40").read()
        subdomains = [line.strip() for line in output.splitlines() if line.strip()]
        sendmessage(f"  [+] {len(subdomains)} subs found for {domain}", colour='GREEN')
        return subdomains
    except Exception as e:
        sendmessage(f"Error running Subfinder on {domain}: {e}", colour='RED')
        return []



def run_httpx(watcher_wildcard , input_file_path):
    try:
        sendmessage(f"[info] Starting HTTPx on '{watcher_wildcard}'...", telegram=False)

        output_file_path = f"{input_file_path}_output.jsonl"

        command = [
            'httpx',
            '-l', input_file_path,
            '-title',
            '-status-code',
            '-tech-detect',
            '-web-server',
            '-ip',
            '-cname',
            '-cdn',
            '-location',
            '-content-length',
            '-tls-probe',
            '-method',
            '-path',
            '-probe',
            '-no-color',
            '-json',
            '-silent',
            '-threads', '50',
            '-timeout', '10',
            '-o', output_file_path
        ]

        # Redirect stdout and stderr to /dev/null to silence the output
        with open(os.devnull, 'w') as devnull:
            subprocess.run(command, check=True, stdout=devnull, stderr=devnull)

        return output_file_path

    except subprocess.CalledProcessError as e:
        sendmessage(f"[error] HTTPx failed: {e}", colour='RED')
        return None


def parse_httpx_jsonl(file_path):
    sendmessage(f"  [*] Starting Parsing Data ...")
    results = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                results.append(data)
            except json.JSONDecodeError:
                continue
    return results



def save_httpx_results(results):
    sendmessage(f"     [+] Starting Save Httpx Results and Detect Changes", colour='GREEN')

    for item in results:
        domain = item.get("input")
        try:
            discovered = DiscoverSubdomain.objects.get(subdomain=domain)
        except DiscoverSubdomain.DoesNotExist:
            continue

        new_data = {
            "httpx_result": item.get("url"),
            "status_code": item.get("status_code"),
            "title": item.get("title"),
            "server": item.get("web_server"),
            "technologies": item.get("technologies") or [],
            "has_ssl": 'True' if item.get("tls", 'False') else 'False',
            "ip_address": item.get("ip"),
            "port": item.get("port"),
            "content_type": item.get("content_type"),
            "content_length": item.get("content_length"),
            "cname": item.get("cname") or [],
            "a_records": item.get("a") or [],
        }

        try:
            existing = SubdomainHttpx.objects.get(discovered_subdomain=discovered)
            change_data = {}

            for field, new_value in new_data.items():
                old_value = getattr(existing, field)
                if old_value != new_value:
                    # ذخیره تغییرات به شکل old_value -> new_value
                    change_data[f"{field}_change"] = f"{old_value} -> {new_value}"

            if change_data:
                # فقط اگر تغییر وجود داشت، بروزرسانی کن و تغییرات را ثبت کن
                obj, created = SubdomainHttpx.objects.update_or_create(
                    discovered_subdomain=discovered,
                    defaults={**new_data}
                )

                if created:
                    obj.label = 'new'
                    obj.save()

                SubdomainHttpxChanges.objects.update_or_create(
                    discovered_subdomain=discovered,
                    defaults={**change_data, "label": "changed"}
                )

            else:
                # اگر تغییری نبود، فیلدها رو همون قبلی‌ها بذار
                if existing:
                    obj = existing  # قبلی رو نگه دار
                else:
                    # اگر رکوردی نبود، بسازش با داده‌های فعلی
                    obj, created = SubdomainHttpx.objects.update_or_create(
                        discovered_subdomain=discovered,
                        defaults={**new_data}
                    )
                    if created:
                        obj.label = 'new'
                        obj.save()

        except SubdomainHttpx.DoesNotExist:
            existing = None

        obj, created = SubdomainHttpx.objects.update_or_create(
            discovered_subdomain=discovered,
            defaults={**new_data}
        )

        if created:
            obj.label = 'new'
            obj.save()



def parse_datetime(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None



def export_for_httpx(subdomains , file):
    try :
        with open (file , 'w') as file:
            file.writelines([f"{s}\n" for s in subdomains])
   
    except Exception as e :
        sendmessage(f"Error Export domains for Httpx {e}" , colour='RED')


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
                clear_subdomains_labels(wildcard)
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
        sendmessage(f"Process Subfinder error: {e}", colour='RED')


def clear_subdomains_labels(watcher):
    DiscoverSubdomain.objects.filter(wildcard=watcher).update(label="available")

def clear_httpx_labels():
    SubdomainHttpx.objects.filter(is_active = True).update(label='available')

def check_a_record(domain: str) -> bool:
    try:
        fake_domain = f"nonexistent1234.{domain}"
        result = pydig.query(fake_domain, 'A')
        if result:
            sendmessage(f"[info] A record verification failed for {domain}", colour='RED')


            return False
        sendmessage(f"[info] A record check passed for {domain}", colour='GREEN')
        return True
    except Exception as e:
        sendmessage(f"DNS A record check error: {e}", colour='RED')
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

            sendmessage(f"[info] Starting DNSBruteforce for {wildcard.wildcard}", telegram=True)
            subdomains = generate_dns_wordlist(asset, wildcard)

            # First Shuffledns
            shuffle_out = f"{OUTPUT_PATH}/shuffle_out.txt"
            cmd = (
                f"shuffledns -d {wildcard.wildcard} -w {WORDLISTS_PATH}/{asset.user.username}/dnsbruteforce_all.txt "
                f"-r {OUTPUT_PATH}/resolvers.txt -o {shuffle_out} -silent"
            )
            os.popen(cmd).read()

            # DNSGen
            dnsgen_in = f"{OUTPUT_PATH}/dnsgen_subs.txt"
            dnsgen_out = f"{OUTPUT_PATH}/dnsgen_out.txt"
            combine_dnsgen_input(shuffle_out, asset, wildcard, dnsgen_in)
            os.popen(f"dnsgen {dnsgen_in} | tee {dnsgen_out}").read()

            # Second Shuffledns
            os.popen(
                f"shuffledns -d {wildcard.wildcard} -w {dnsgen_out} -r {OUTPUT_PATH}/resolvers.txt -o {OUTPUT_PATH}/dns_gen_shuffle_out.txt -silent"
            ).read()

            # Save results
            save_discovered_subs([shuffle_out, dnsgen_out], wildcard, dns_tool)
            wildcard.status = 'completed'
            wildcard.save()
            sendmessage(f"[done] DNSBrute completed for {asset}", colour='GREEN')


def generate_dns_wordlist(asset, wildcard):
    discovered_file = f"{WORDLISTS_PATH}/{asset.user.username}/dnsbruteforce_discovered.txt"
    combined_file = f"{WORDLISTS_PATH}/{asset.user.username}/dnsbruteforce_all.txt"

    subfinder_subs = run_subfinder(wildcard.wildcard)
    clean_subs = [s.replace(f".{wildcard.wildcard}", '') for s in subfinder_subs if s]

    with open(discovered_file, 'w') as f:
        f.writelines([f"{s}\n" for s in clean_subs])

    with open(asset.dns_bruteforce_wordlist.path, 'r') as f:
        static_words = [line.strip() for line in f if line.strip()]

    combined = set(clean_subs + static_words)
    with open(combined_file, 'w') as f:
        f.writelines([f"{word}\n" for word in combined])

    sendmessage(f"[info] {len(combined)} subdomains collected for DNS bruteforce", colour='GREEN')
    return combined


def combine_dnsgen_input(shuffle_result_path, asset, wildcard, output_file):
    with open(shuffle_result_path, 'r') as f:
        shuffle_subs = [line.strip().replace(f".{wildcard.wildcard}", '') for line in f if line.strip()]

    discovered_file = f"{WORDLISTS_PATH}/{asset.user.username}/dnsbruteforce_discovered.txt"
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



def process_httpx(assets_watchers):
    clear_httpx_labels()
    subdomains_httpx = f"{OUTPUT_PATH}/subdomains_httpx.txt"
    for assets_watcher in assets_watchers:
        for watcher_wildcard in assets_watcher.wildcards.all():
            for tool in watcher_wildcard.tools.all():
                if tool.tool_name == 'httpx':
                    subdomains = DiscoverSubdomain.objects.filter(wildcard=watcher_wildcard).values_list('subdomain', flat=True)
                    export_for_httpx(subdomains, subdomains_httpx)
                    output_file = run_httpx(watcher_wildcard,subdomains_httpx)
                    if output_file:
                        results = parse_httpx_jsonl(output_file)
                        save_httpx_results(results)

  

@shared_task
def check_assets():
    assets = AssetWatcher.objects.filter(is_active=True)
    AssetWatcher.objects.filter(is_active=True).update(status='pending')

    subfinder_domains = set()
    httpx_domains = set()
    for asset in assets:
        try:
            for wildcard in asset.wildcards.all():
                wildcard.status = 'pending'
                wildcard.save()

                for tool in wildcard.tools.all():
                    if tool.tool_name == 'subfinder':
                        subfinder_domains.add(wildcard.wildcard)
                    if tool.tool_name =='httpx':
                        httpx_domains.add(wildcard.wildcard)

        except Exception as e:
            asset.status = 'failed'
            asset.save()
            sendmessage(f"[error] Failed to process {asset}: {e}", colour='RED')

    try:
        pass
        process_subfinder(subfinder_domains)
        # process_dns_bruteforce(assets)
        process_httpx(assets)
    except Exception as e:
        sendmessage(f"[error] Subdomain discovery failed: {e}", colour='RED')

    AssetWatcher.objects.filter(is_active=True).update(status='completed')