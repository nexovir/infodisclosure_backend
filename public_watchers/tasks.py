from celery import shared_task
from .models import ProgramWatcher
from django.utils.timezone import now
import colorama , json , requests , time , subprocess
from requests.exceptions import RequestException
from .models import *



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




def request(url: str, name:str ,  retries: int = 20, delay: int = 5) -> dict:
    sendmessage (f"[info] Getting {name} data ..." )
    attempts = 0
    while attempts < retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            sendmessage(f"      [info] Connection OK" , colour='GREEN')
            return data
        except (RequestException, json.JSONDecodeError) as e:
            sendmessage(f"  [error] Failed to retrieve data: {e}. Retrying in {delay} seconds...", colour='RED')
            attempts += 1
            time.sleep(delay)
        except Exception as e:
            sendmessage(f"  [error] An unexpected error occurred: {e}" , colour='RED')
            break
    sendmessage(f"  [error] Failed to retrieve data after {retries} attempts." , colour='RED')
    return None




def delete_label (watcherprogram):
    try : 
        program_obj = DiscoverdProgram.objects.filter(watcher = watcherprogram)
        program_obj.update(label = "available")
        DiscoverdScope.objects.filter(discovered_program__in=program_obj).update(label='available')
    except Exception as e :
        sendmessage(f"  [error] error while deleting label {e}", colour='RED')




def get_bugcrowd_programs(data, watcherprogram):
    def map_asset_type(asset_type):
        if asset_type == 'website':
            return 'web'
        elif asset_type == 'api':
            return 'api'
        elif asset_type == 'hardware':
            return 'iot'
        elif asset_type in ['ios', 'android']:
            return 'mobile'
        else:
            return 'others'

    def save_scope(program_obj, item, scope_type):
        obj, created = DiscoverdScope.objects.update_or_create(
            discovered_program=program_obj,
            name=item.get('name', ''),
            defaults={
                'type': map_asset_type(item.get('type')),
                'scope_type': scope_type
            }
        )
        if created:
            obj.label = 'new'
            obj.save()
    try:
        for program in data:
            program_obj, created = DiscoverdProgram.objects.update_or_create(
                name=program.get("name", ""),
                defaults={
                    "watcher": watcherprogram,
                    "url": program.get("url", ""),
                    "type": 'vdp' if program.get("allows_disclosure") else 'rdp'
                }
            )

            if created:
                program_obj.label = "new"
                program_obj.save()

            for item in program.get("targets", {}).get("in_scope", []):
                try:
                    save_scope(program_obj, item, 'in_scope')
                except Exception as e:
                    sendmessage(f"  [error] in_scope error: {e}", colour='RED')

            for item in program.get("targets", {}).get("out_of_scope", []):
                try:
                    save_scope(program_obj, item, 'out_of_scope')
                except Exception as e:
                    sendmessage(f"  [error] out_of_scope error: {e}", colour='RED')

        sendmessage('       [+] Bugcrowd Data Inserting Successfully', colour='GREEN')

    except Exception as e:
        sendmessage(f'  [error] Error: {e}', colour='RED')





def get_hackerone_programs(data, watcherprogram):
    def map_asset_type(asset_type):
        if asset_type == 'AI_MODEL':
            return 'ai_model'
        elif asset_type == 'API':
            return 'api'
        elif asset_type in ['APPLE_STORE_APP_ID', 'GOOGLE_PLAY_APP_ID', 'WINDOWS_APP_STORE_APP_ID', 'OTHER_APK', 'OTHER_IPA', 'TESTFLIGHT']:
            return 'mobile'
        elif asset_type in ['CIDR', 'IP_ADDRESS']:
            return 'infrastructure'
        elif asset_type == 'HARDWARE':
            return 'iot'
        elif asset_type == 'SMART_CONTRACT':
            return 'web3'
        elif asset_type == 'DOWNLOADABLE_EXECUTABLES':
            return 'desktop'
        elif asset_type == 'WILDCARD':
            return 'wildcard'
        elif asset_type == 'URL':
            return 'web'
        elif asset_type == 'SOURCE_CODE':
            return 'code'
        else:
            return 'others'

    def save_scope(program_obj, item, scope_type):
        obj, created = DiscoverdScope.objects.update_or_create(
            discovered_program=program_obj,
            name=item.get('asset_identifier', ''),
            defaults={
                'type': map_asset_type(item.get('asset_type')),
                'scope_type': scope_type
            }
        )
        if created:
            obj.label = 'new'
            obj.save()
    try:
        for program in data:
            program_obj, created = DiscoverdProgram.objects.update_or_create(
                name=program.get("name", ""),
                defaults={
                    "watcher": watcherprogram,
                    "url": program.get("url", ""),
                    "type": 'rdp' if program.get("offers_bounties") else 'vdp'
                }
            )

            if created:
                program_obj.label = "new"
                program_obj.save()

            for item in program.get("targets", {}).get("in_scope", []):
                try:
                    save_scope(program_obj, item, 'in_scope')
                except Exception as e:
                    sendmessage(f"  [error] in_scope error: {e}", colour='RED')

            for item in program.get("targets", {}).get("out_of_scope", []):
                try:
                    save_scope(program_obj, item, 'out_of_scope')
                except Exception as e:
                    sendmessage(f"  [error] out_of_scope error: {e}", colour='RED')

        sendmessage('       [+] Hackerone Data Inserting Successfully', colour='GREEN')

    except Exception as e:
        sendmessage(f"  [error] Error: {e}", colour='RED')



def get_federacy_programs(data, watcherprogram):
    def map_asset_type(asset_type):
        if asset_type == 'api':
            return 'api'
        elif asset_type == 'desktop':
            return 'desktop'
        elif asset_type == 'mobile':
            return 'mobile'
        elif asset_type == 'website':
            return 'web'
        else:
            return 'others'
        
        
    def save_scope(program_obj, item, scope_type):
        obj, created = DiscoverdScope.objects.update_or_create(
            discovered_program=program_obj,
            name=item.get('target', ''),
            defaults={
                'type': map_asset_type(item.get('type')),
                'scope_type': scope_type
            }
        )
        if created:
            obj.label = 'new'
            obj.save()

    try:
        for program in data:
            program_obj, created = DiscoverdProgram.objects.update_or_create(
                name=program.get("name", ""),
                defaults={
                    "watcher": watcherprogram,
                    "url": program.get("url", ""),
                    "type": 'rdp' if program.get("offers_awards") else 'vdp'
                }
            )

            if created:
                program_obj.label = "new"
                program_obj.save()

            for item in program.get("targets", {}).get("in_scope", []):
                try:
                    save_scope(program_obj, item, 'in_scope')
                except Exception as e:
                    sendmessage(f"  [error] in_scope error: {e}", colour='RED')

            for item in program.get("targets", {}).get("out_of_scope", []):
                try:
                    save_scope(program_obj, item, 'out_of_scope')
                except Exception as e:
                    sendmessage(f"  [error] out_of_scope error: {e}", colour='RED')

        sendmessage('       [+] Federacy Data Inserting Successfully', colour='GREEN')

    except Exception as e:
        sendmessage(f"  [error] Error: {e}", colour='RED')




def get_intigriti_programs (data, watcherprogram):
    def map_asset_type(asset_type):
        if asset_type in ['android' , 'ios']:
            return 'mobile'
        elif asset_type == 'device':
            return 'iot'
        elif asset_type == 'iprange':
            return 'infrastructure'
        elif asset_type == 'url':
            return 'web'
        elif asset_type == 'wildcard':
            return 'wildcard'
        else:
            return 'others'
        
        
    def save_scope(program_obj, item, scope_type):
        obj, created = DiscoverdScope.objects.update_or_create(
            discovered_program=program_obj,
            name=item.get('endpoint', ''),
            defaults={
                'type': map_asset_type(item.get('type')),
                'scope_type': scope_type
            }
        )
        if created:
            obj.label = 'new'
            obj.save()

    try:
        for program in data:
            program_obj, created = DiscoverdProgram.objects.update_or_create(
                name=program.get("name", ""),
                defaults={
                    "watcher": watcherprogram,
                    "url": program.get("url", ""),
                    "type": "rdp" if program.get("min_bounty", {}).get("value", 0) > 0 else "vdp",
                }
            )

            if created:
                program_obj.label = "new"
                program_obj.save()

            for item in program.get("targets", {}).get("in_scope", []):
                try:
                    save_scope(program_obj, item, 'in_scope')
                except Exception as e:
                    sendmessage(f"  [error] in_scope error: {e}", colour='RED')

            for item in program.get("targets", {}).get("out_of_scope", []):
                try:
                    save_scope(program_obj, item, 'out_of_scope')
                except Exception as e:
                    sendmessage(f"  [error] out_of_scope error: {e}", colour='RED')

        sendmessage('       [+] Intigriti Data Inserting Successfully', colour='GREEN')

    except Exception as e:
        sendmessage(f"  [error] Error: {e}", colour='RED')




def get_yeswehack_programs (data, watcherprogram):
    def map_asset_type(asset_type , target):
        if asset_type in ['mobile-application' , 'mobile-application-android' , 'mobile-application-ios' , 'application']:
            return 'mobile'
        elif asset_type == 'api':
            return 'api'
        elif asset_type == 'web-application':
            return 'web'
        elif '*' in target:
            return 'wildcard'
        else:
            return 'others'
        
        
    def save_scope(program_obj, item, scope_type):
        obj, created = DiscoverdScope.objects.update_or_create(
            discovered_program=program_obj,
            name=item.get('target', ''),
            defaults={
                'type': map_asset_type(item.get('type') , item.get('target')),
                'scope_type': scope_type
            }
        )
        if created:
            obj.label = 'new'
            obj.save()
    try:
        for program in data:
            program_obj, created = DiscoverdProgram.objects.update_or_create(
                name=program.get("name", ""),
                defaults={
                    "watcher": watcherprogram,
                    "url": program.get("url", ""),
                    "type": "vdp" if program.get("min_bounty")=="null" else "rdp",
                }
            )

            if created:
                program_obj.label = "new"
                program_obj.save()

            for item in program.get("targets", {}).get("in_scope", []):
                try:
                    save_scope(program_obj, item, 'in_scope')
                except Exception as e:
                    sendmessage(f"  [error] in_scope error: {e}", colour='RED')

            for item in program.get("targets", {}).get("out_of_scope", []):
                try:
                    save_scope(program_obj, item, 'out_of_scope')
                except Exception as e:
                    sendmessage(f"  [error] out_of_scope error: {e}", colour='RED')

        sendmessage('       [+] Yeswehack Data Inserting Successfully', colour='GREEN')

    except Exception as e:
        sendmessage(f"  [error] Error: {e}", colour='RED')




@shared_task
def check_programs():

    watcherprograms = ProgramWatcher.objects.filter(is_active = True)
    ProgramWatcher.objects.filter(is_active = True ).update(status='pending')

    for program in watcherprograms :
        try : 
            data = request(program.platform_url , program.platform_name)
            program.status = 'running'
            program.save()
            delete_label(program)
            if program.platform_name == 'Bugcrowd':
                get_bugcrowd_programs(data , program)

            if program.platform_name == 'Hackerone':
                get_hackerone_programs(data , program)

            if program.platform_name == 'Federacy':
                get_federacy_programs(data ,program)

            if program.platform_name == 'Intigriti':
                get_intigriti_programs(data, program)

            if program.platform_name == 'Yeswehack':
                get_yeswehack_programs (data , program)

            program.status = 'completed'
            program.save()

        except TypeError as e :
            program.status = 'failed'
            program.save()
            
            sendmessage(f'Error : {e}' , colour='RED')