from celery import shared_task
from django.utils.timezone import now 
import colorama , json , requests , time , subprocess , pydig
from requests.exceptions import RequestException
from .models import *
import os 


def sendmessage (message : str , telegram : bool = False, colour : str = "YELLOW" , logger : bool = True):
    color = getattr(colorama.Fore, colour, colorama.Fore.YELLOW)
    print(color + message + colorama.Style.RESET_ALL)
    named_tuple = time.localtime() # get struct_time
    time_string = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
    if logger == True :
        with open ('logger.txt' , 'a') as file :
            file.write (message+' -> '+ time_string+'\n')
    if telegram == True :
        message = message.replace(' ','+')
        command = f'curl -X POST "https://api.telegram.org/bot6348870305:AAHawStCiN6XfiAu_ZwQJU-x8C1XtKjZ2XA/sendMessage" -d "chat_id=5028701156&text={message}"'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()  




def proccess_subfinder(domains):
    def subfinder(domain):
        try:
            sendmessage(f"Starting Subfinder for '{domain}' Please Wait ...", telegram=True, logger=True)
            subs = os.popen(f"subfinder -d {domain} -silent -timeout 20 -max-time 20").read()
            new_subs = [sub.strip() for sub in subs.split('\n') if sub.strip()]
            sendmessage(f"    [info] {len(new_subs)} subs for {domain} discovered", colour='GREEN')
            return new_subs
        except Exception as e:
            sendmessage(f"Error executing Subfinder on {domain}: {e}", colour='RED')
            return []

    try:
        subfinder_tool = Tool.objects.get(tool_name='subfinder')

        for domain in domains:
            watched_wildcards = WatchedWildcard.objects.filter(
                is_active=True,
                tools__tool_name='subfinder',
                wildcard=domain
            )

            for watched_wildcard in watched_wildcards:
                watched_wildcard.status = 'running'
                watched_wildcard.save()

            try:
                subs = subfinder(domain)

                for watched_wildcard in watched_wildcards:
                    delete_label(watched_wildcard)

                    for sub in subs:
                        obj, created = DiscoverSubdomain.objects.update_or_create(
                            wildcard=watched_wildcard,
                            subdomain=sub,
                            defaults={'tool': subfinder_tool}
                        )
                        if created:
                            obj.label = "new"
                            obj.save()

                    watched_wildcard.status = 'completed'
                    watched_wildcard.save()

            except Exception as inner_error:
                sendmessage(f"Error during processing domain {domain}: {inner_error}", colour='RED')
                for watched_wildcard in watched_wildcards:
                    watched_wildcard.status = 'failed'
                    watched_wildcard.save()

    except Exception as e:
        sendmessage(f"Error at Process Subfinder (general): {e}", colour='RED')







def proccess_dns_bruteforce(domains):

    def check_a_record(domain : str) -> bool:

        sendmessage (f"Checking For {domain} Arecord ...")
        full_domain = "somedomaindosentexist." + domain
        try:
            result = pydig.query(full_domain, 'A')
            
            if result:
                sendmessage(f"verification faild" , colour='RED')
                return False

            else:
                sendmessage(f"verification was successfully done" , colour='GREEN')
                return True
                
        except Exception as e:
            sendmessage(f"Error check a record {e}" , colour='RED')

    

    def create_dnsgen_subs (shuffledns : list , domain : str):

        sub_subdomains = []
        with open ('outputs/sub-subdomains.txt' , 'r') as file :
            for line in file :
                sub_subdomains.append(line.strip())
                
        for i in range(len(shuffledns)) :
            shuffledns[i] = shuffledns[i].strip().replace (f'.{domain}' , '')
        dns_gen_subs = set(shuffledns+sub_subdomains)
        
        with open ('outputs/dns_gen.subs' , 'w') as file :
            for sub in set(dns_gen_subs) :
                file.write(sub+'\n')



    def add_to_file (dns_bruteforce_discoverd : list):

        filename = 'subs/subfinder.subs'
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                existing_lines = {line.strip() for line in file}
            
            with open(filename, 'a', encoding='utf-8') as file:
                for string in dns_bruteforce_discoverd:
                    if string not in existing_lines:
                        file.write(string + '\n')
                    else:
                        pass
        except FileNotFoundError:
            sendmessage(f"File {filename} not found. Please check the path.")
        except Exception as e:
            sendmessage(f"An error occurred: {e}")



    def get_subdomains (domain : str):
        subdomains = []

        # WordList Discoverd from Domain

        old_subs = set(DiscoverSubdomain.objects.filter(wildcard__wildcard=domain).values_list('subdomain', flat=True))

        for old_sub in old_subs :
            subdomains.append(old_sub.replace(f'.{domain}',''))

        with open ('private_watchers/wordlists/sub-subdomains.txt' , 'w') as file:
            for sub in subdomains :
                file.write(sub+'\n')
        

        # Wordlist Discoverd from StaticWordlist
        
        with open ('private_watchers/wordlists/2m-subdomains.subs' , 'r') as file :
            for line in file :
                subdomains.append (line.strip())

        # with open ('outputs/all-subdomains.txt' , 'w') as file:
        #     for sub in set(subdomains) :
        #         file.write(sub+'\n')
        
        # sendmessage (color.WHITE + f"Found {color.RED}{len(set(subdomains))}{color_reset} {color.WHITE}subdomains from {color.YELLOW}subs.subs and 2m-subdomains.subs{color_reset}" , telegram=False , colour="GREEN")
        
        # return (set(subdomains))
    



    for domain in domains :
        if (check_a_record(domain)):
            sendmessage(f"Starting DNSBruteforce at {domain}" , telegram=True)
            print(domain)
            subdomains = get_subdomains (domain)
            # for subdomain in subdomains :
            #     print(subdomain)
            # sendmessage (f'Starting Shuffledns on Discoverd Subs & Static Wordlist ...')
            # resolve1 = os.popen("shuffledns -d "+ domain +" -w outputs/all-subdomains.txt  -r outputs/resolvers.txt -o outputs/shuffle_out.txt -silent").read()
            # resolve1 = resolve1.split('\n')

            # sendmessage (f'Starting DnsGen ...')
            # create_dnsgen_subs (resolve1 , domain)
            
    #         os.popen("dnsgen outputs/dns_gen.subs | tee outputs/dns_gen_out.subs").read()


    #         sendmessage (f'{color.WHITE}Starting Shuffledns on {color.YELLOW}DnsGen ...{color_reset}')

    #         resolve2 = os.popen("shuffledns -d "+single_domain+" -w outputs/dns_gen_out.subs  -r outputs/resolvers.txt  -o outputs/dns_gen_shuffle_out.txt -silent").read() 

    #         sendmessage (f'{color.WHITE}Saveing...{color_reset}')

    #         final = []
    #         with open ('outputs/shuffle_out.txt' , 'r') as file :
    #             for line in file :
    #                 final.append(line.strip())
    #         with open ('outputs/dns_gen_shuffle_out.txt' , 'r') as file :
    #             for line in file :
    #                 final.append(line.strip())
            
    #         final = set(final)
            
    #         cursor.execute(f"SELECT {single_domain.replace('.', '_').replace('-','_')} FROM ASSETS")
    #         existing_values = {row[0] for row in cursor.fetchall()}
            
    #         for item in final:
    #             if item not in existing_values:
    #                 print(single_domain.replace('.', '_').replace('-','_'))
    #                 cursor.execute(f"INSERT INTO ASSETS ({single_domain.replace('.', '_').replace('-','_')}) VALUES (?)", (item,))
                    
    #                 sendmessage(f"[+] '{item}'  -> [DNSbruteforce discoverd]" ,telegram=False , colour="GREEN")
    #             else :
    #                 sendmessage(f"[-] '{item}'  -> [exists in database]" ,telegram=False , colour="RED")
    #         conn.commit()


    #     else :
    #         pass
    
    # named_tuple = time.localtime() # get struct_time
    # time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple) 
    # sendmessage (f'DnsBrute Was Successfully done at -> {time_string}' , telegram=True , logger=True)






def delete_label (watcherprogram):
    DiscoverSubdomain.objects.filter(wildcard = watcherprogram).update(label = "available")




@shared_task
def check_assets():
    watcher_assets = AssetWatcher.objects.filter(is_active=True)
    AssetWatcher.objects.filter(is_active=True).update(status='pending') 

    subfinder_domains = []
    amass_domains = []
    dns_bruteforce_domains = []

    for asset_watcher in watcher_assets:
        try:
            for asset in asset_watcher.wildcards.all():
                asset.status = 'running'
                asset.save()

                for tool in asset.tools.all():
                    if tool.tool_name == 'subfinder' and asset.wildcard not in subfinder_domains:
                        subfinder_domains.append(asset.wildcard)
                    elif tool.tool_name == 'amass' and asset.wildcard not in amass_domains:
                        amass_domains.append(asset.wildcard)
                    elif tool.tool_name == 'dns_bruteforce' and asset.wildcard not in dns_bruteforce_domains:
                        dns_bruteforce_domains.append(asset.wildcard)

        except Exception as e:
            asset_watcher.status = 'failed'
            asset_watcher.save()
            sendmessage(f'error in getting data from watchers: {e}', colour='RED')

    try:
        # proccess_subfinder(subfinder_domains)
        proccess_dns_bruteforce (dns_bruteforce_domains , watcher_assets)


    except Exception as e:
        asset_watcher.status = 'failed'
        asset_watcher.save()
        sendmessage(f'error in process for discover new subs: {e}', colour='RED')

    AssetWatcher.objects.filter(is_active=True).update(status='completed')
