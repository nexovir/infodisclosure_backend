from celery import shared_task
from .models import ProgramWatcher
from django.utils.timezone import now 
import colorama , json , requests , time , subprocess
from requests.exceptions import RequestException
from .models import ProgramWatcher , DiscoverdProgram


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



def request(url: str, retries: int = 20, delay: int = 5) -> dict:

    attempts = 0
    while attempts < retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            sendmessage(f"Connection OK" , colour='GREEN')
            return data
        except (RequestException, json.JSONDecodeError) as e:
            sendmessage(f"Failed to retrieve data: {e}. Retrying in {delay} seconds...", colour='RED')
            attempts += 1
            time.sleep(delay)
        except Exception as e:
            sendmessage(f"An unexpected error occurred: {e}" , colour='RED')
            break
    sendmessage(f"Failed to retrieve data after {retries} attempts." , colour='RED')
    return None



def get_bugcrowd_programs(data , watcherprogram):
    try : 
        for program in data :
            DiscoverdProgram.objects.get_or_create(
                watcher = watcherprogram,
                name = program.get("name" , ""),
                url = program.get("url" , ""),
                type = "rdp" if program.get("allows_disclosure") is True else "vdp" if program.get("allows_disclosure") is False else "others",
            )
        sendmessage ('Bugcrowd Data Inserting Successfully' , colour='GREEN')
    except Exception as e :
        sendmessage (f'Erorr as {e}' , colour='RED')


def get_hackerone_programs(data , program):
    pass
    


@shared_task
def check_programs():
    watcherprograms = ProgramWatcher.objects.filter(is_active = True)
    for program in watcherprograms :

        try : 
            data = request(program.platform_url)
            
            if program.platform_name == 'Bugcrowd':
                get_bugcrowd_programs(data , program)

            if program.platform_name == 'Hackerone':
                get_hackerone_programs(data , program)
        
        except TypeError as e :
            sendmessage(f'Error : {e}' , colour='RED')