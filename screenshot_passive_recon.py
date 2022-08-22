from rich.console import Console
from ipwhois import IPWhois
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from time import sleep
from urllib.parse import unquote
import argparse
import socket
import whois
import requests


def screenshot(screen_name, url):
    # Random User-Agent to try avoiding Captcha
    # https://stackoverflow.com/questions/68772211/fake-useragent-module-not-connecting-properly-indexerror-list-index-out-of-ra
    options = Options()
    options.add_argument("window-size=1920,1080")

    # Choose a random user agent
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    # No cache
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", False)
    options.set_preference("browser.cache.offline.enable", False)
    options.set_preference("network.http.use-cache", False) 

    # Default language en-US
    options.set_preference("intl.accept_languages", "en,en-US")

    # Force private browsing
    options.set_preference("browser.privatebrowsing.autostart", True)

    driver = webdriver.Firefox(firefox_options=options, service_log_path='/dev/null')

    # Delete all cookies
    driver.delete_all_cookies()

    # Screenshot
    driver.get(url)
    sleep(1)
    print("Screenshoting " + screen_name)

    # Accept the "Before you continue to Google"
    if url.startswith('https://www.google.com/'):
        ActionChains(driver)\
        .send_keys(Keys.TAB)\
        .send_keys(Keys.TAB)\
        .send_keys(Keys.TAB)\
        .send_keys(Keys.TAB)\
        .send_keys(Keys.TAB)\
        .send_keys(Keys.ENTER)\
        .perform()

    sleep(1)
    driver.get_screenshot_as_file(screen_name + ".png")
    driver.quit()

def download(dl_name, url):
    console.print("Downloading " + dl_name)
    r = requests.get(url)
    img = r.content 
    with open(dl_name + '.png', 'wb') as handler:
        handler.write(img)

def shodan(ipx):
	for ip in ipx:
		url = 'https://www.shodan.io/host/' + ip 
		screen_name = 'shodan_' + ip.replace('.','_')
		screenshot(screen_name, url)

def censys(ipx):
	for ip in ipx:
		url = 'https://search.censys.io/hosts/' + ip 
		screen_name = 'censys_' + ip.replace('.','_')
		screenshot(screen_name, url)

# https://stackoverflow.com/questions/3837744/how-to-resolve-dns-in-python
def getIPx(d):
    """
    This method returns an array containing
    one or more IP address strings that respond
    as the given domain name
    """
    try:
        data = socket.gethostbyname_ex(d)
        ipx = data[2]
        return ipx
    except Exception:
        # fail gracefully!
        return False

def whois_info(d):
    # Can provide information about a domain name, such as the name server and registrar.
    whois_result = whois.query(d)
    return whois_result.__dict__

def whois_extensive(ipx):
    # https://ipwhois.readthedocs.io/en/latest/RDAP.html
    for ip in ipx:
        whois_extensive_result = IPWhois(ip)
        # Full output : 
        # pprint(whois_extensive_result.lookup_rdap(depth=1))
        whois_extensive_dict = whois_extensive_result.lookup_rdap(depth=1)
        whois_extensive_dict_obj = whois_extensive_dict['objects']
        return whois_extensive_dict_obj
            
def dnsdumpster(d):
    #https://dnsdumpster.com/static/map/domain.tld.png
    url = 'https://dnsdumpster.com/static/map/' + d +'.png'
    download('dnsdumpster_' + d, url)

def pastebin(d):
    #site:pastebin.com "domain"
    #https://www.google.com/search?q=site%3Apastebin.com+"domain"
    short_domain = d.split('.')[-2]
    url = 'https://www.google.com/search?q=site%3Apastebin.com+"' + short_domain + '"&hl=en'
    screenshot("pastebin_" + short_domain, url)

def google_dorks(d):
    # custom + inspired by : https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/03-Test_File_Extensions_Handling_for_Sensitive_Information
    extensions = [ "asa", "inc", "config", "zip", "tar", "gz", "tgz", "rar", "java", "txt", "pdf", "doc", "docx", "rtf", "xls", "xlsx", "ppt", "pptx", "bak", "old", "swp", "~", "odp", "ods" ]
    # https://stackoverflow.com/questions/531269/how-do-i-search-for-multiple-file-types-on-google-search-appliance
    url = 'https://www.google.com/search?q=site%3A"' + d + '"+'
    for ext in extensions:
        url += "filetype%3A" + ext + "+OR+"
        if ext == extensions[-1]:
            url += "filetype%3A" + ext
    url += "&hl=en"
    console.print("URL : " + unquote(url).replace('+',' '), highlight=False)
    screenshot("dorks_" + d, url) 

def netcraft_site(d):
    # https://sitereport.netcraft.com/?url=https://domain.tld
    url = 'https://sitereport.netcraft.com/?url=https://' + d
    screenshot("netcraft_site_" + d, url)

def netcraft_dns(d):
    # https://searchdns.netcraft.com/?restriction=site+contains&host=.domain.tld&position=limited
    url = 'https://searchdns.netcraft.com/?restriction=site+contains&host=.' + d + '&position=limited'
    screenshot("netcraft_dns_" + d, url)

def netcraft_neighbours(d):
    # https://sitereport.netcraft.com/netblock?url=domain.tld
    url = 'https://sitereport.netcraft.com/netblock?url=' + d
    screenshot("netcraft_neighbours_" + d, url)

def crt_sh(d):
    # https://crt.sh/?q=domain.tld
    url = 'https://crt.sh/?q=' + d
    screenshot("crt_sh_" + d, url)

def intelx(d):
    # https://intelx.io/?s=domain.tld
    url = 'https://intelx.io/?s=' + d
    screenshot("intelx_" + d, url)

# Main program

if __name__ == "__main__":

    console = Console()

    parser = argparse.ArgumentParser(description="Passive reconnaissance tool")
    parser.add_argument("-d", "--domain", help="Target domain", type=str, required=True)
    args = parser.parse_args()

    domain = args.domain
    console.print("[+] Domain : " + domain, style="green")


    ## Get IPs
    console.print("[+] IP : " + repr(getIPx(domain)), style="green")
    ipx = getIPx(domain)

    ## Quick Whois
    try:
        # could failed and exit if not a well known top level domain
        whois_dict = whois_info(domain)
        console.print("[+] Whois (Domain based): ", style="green")
        for key in whois_dict.keys():
            print(key + ":", whois_dict[key])
    except:
        # for example .lu domain failed so skip this part
        pass

    ## Extensive Whois
    console.print("[+] Extensive Whois (IP based): ", style="green")
    whois_ext_dict = whois_extensive(ipx)
    for key in whois_ext_dict:
        if whois_ext_dict[key]['contact'] != None:
            console.print(whois_ext_dict[key]['contact'], highlight=False)

    ## Shodan
    console.print("[+] Shodan : ", style="green")
    shodan(ipx)

    ## Censys
    console.print("[+] Censys : ", style="green")
    censys(ipx)

    ## DNSDumpster
    console.print("[+] DNSDumpster : ", style="green")
    dnsdumpster(domain)

    ## Pastebin
    console.print("[+] Pastebin : ", style="green")
    pastebin(domain)

    ## Dorks (sensitive files)
    console.print("[+] Google dorks : ", style="green")
    google_dorks(domain)

    ## Crt.sh
    console.print("[+] Crt.sh : ", style="green")
    crt_sh(domain)

    ## Intelx.io
    console.print("[+] Intelx.io : ", style="green")
    intelx(domain)

    ## Netcraft (too long for the moment)
    console.print("[+] Netcraft : ", style="green")
    console.print("    Websites : ", style="blue")
    netcraft_site(domain)
    console.print("    Subdomains : ", style="blue")
    netcraft_dns(domain)
    console.print("    Neighbours : ", style="blue")
    netcraft_neighbours(domain)
