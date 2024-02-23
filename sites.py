import os
import json
import re


def load_sites():
    if not os.path.isfile('sites.json'):
        with open('sites.json', 'w') as file:
            file.write('[]')

    with open('sites.json', 'r') as file:
        sites = json.loads(file.read())

    return sites


def get_info():
    sites = load_sites()
    if not sites:
        return {
            'total_sites': 0,
            'active_sites': 0
        }

    total_sites = len(sites)
    active_sites = 0
    for site in sites:
        if site['active']:
            active_sites += 1

    return {
        'total_sites': total_sites,
        'active_sites': active_sites
    }
    
def get_site(name):
    sites = load_sites()
    for site in sites:
        if site['name'] == name:
            return site
    return False

def add_site(name, domain):
    sites = load_sites()
    domain = domain.lower().strip()
    # Check domain
    if re.search(r'[^a-zA-Z0-9.-]', domain):
        return False
    
    # Make sure certs directory exists
    if not os.path.isdir('certs'):
        os.mkdir('certs')
    
    if is_icann(domain):
        tlsa = "Not needed"
    else:
        # Generate TLSA record
        tlsa = os.popen(f'./tlsa.sh {domain}').read().strip()
        print(tlsa)
        if not tlsa:
            return False

    id = len(sites)
    for site in sites:
        if site['id'] >= id:
            id = site['id'] + 1

    sites.append({
        'name': name,
        'domain': domain,
        'active': False,
        'tlsa': tlsa,
        'id': id
    })

    with open('sites.json', 'w') as file:
        file.write(json.dumps(sites))
    return True

def add_alt_domain(name, domain):
    sites = load_sites()
    for site in sites:
        if site['name'] == name:
            if 'alt_domains' not in site:
                site['alt_domains'] = []
            site['alt_domains'].append(domain)

            if is_icann(domain):
                tlsa = "Not needed"
            else:
                # Generate TLSA record
                tlsa = os.popen(f'./tlsa.sh {domain}').read().strip()
                print(tlsa)
                if not tlsa:
                    return False
            
            if 'alt_tlsa' not in site:
                site['alt_tlsa'] = {}
            site['alt_tlsa'][domain] = tlsa

            with open('sites.json', 'w') as file:
                file.write(json.dumps(sites))
            return True
    return False

def enable(name, enable):
    sites = load_sites()
    if enable == 'on':
        enable = True
        # Create site file
        write_nginx_conf(name)
    else:
        enable = False
        # Delete site file        
        os.remove(f'/etc/nginx/sites-enabled/{name}')
        


    for site in sites:
        if site['name'] == name:
            site['active'] = enable
            with open('sites.json', 'w') as file:
                file.write(json.dumps(sites))
            return True
    return False

def get_content(site):
    site = get_site(site)
    id = site['id']

    path = f'/var/www/{id}'
    if not os.path.isdir(path):
        return []
    files = os.listdir(path)
    return files

def get_dns_info(site):
    # Get public ip of server
    public_ip = os.popen('curl ipinfo.io/ip').read().strip()
    # Get domains
    domains = get_site(site)
    if not domains:
        return False
    main = domains['domain']
    tlsa = domains['tlsa']
    alt = []
    if 'alt_domains' in domains:
        alt = domains['alt_domains']
    
    info = [{
        'domain': main,
        'ip': public_ip,
        'tlsa': tlsa
    }]


    for alt_domain in alt:
        alt_tlsa = domains['alt_tlsa'][alt_domain]

        info.append({
            'domain': alt_domain,
            'ip': public_ip,
            'tlsa': alt_tlsa
        })
    return info
        

def write_nginx_conf(site):
    site = get_site(site)
    domain = site['domain']
    id = site['id']
    location = f'/var/www/{id}'

    ssl = ""
    if not is_icann(domain):
        ssl = f'''
        listen 443 ssl;
        ssl_certificate /root/site-manager/certs/{domain}/cert.crt;
        ssl_certificate_key /root/site-manager/certs/{domain}/cert.key;
        '''


    conf = f'''
    server {{
  listen 80;
  listen [::]:80;
  root '{location}';
  index index.html;
  server_name {domain} *.{domain};

    location / {{
        try_files $uri $uri/ @htmlext;
    }}

    location ~ \.html$ {{
        try_files $uri =404;
    }}

    location @htmlext {{
        rewrite ^(.*)$ $1.html last;
    }}
    error_page 404 /404.html;
    location = /404.html {{
            internal;
    }}
    location = /.well-known/wallets/HNS {{
        add_header Cache-Control 'must-revalidate';
        add_header Content-Type text/plain;
    }}
    {ssl}
    }}
    '''

    # Add alt domains
    if 'alt_domains' in site:
        for alt in site['alt_domains']:
            if not is_icann(alt):
                ssl = f'''
                listen 443 ssl;
                ssl_certificate /root/site-manager/certs/{alt}/cert.crt;
                ssl_certificate_key /root/site-manager/certs/{alt}/cert.key;
                '''
            else:
                ssl = ""

            conf += f'''
            server {{
    listen 80;
    listen [::]:80;
    root '{location}';
    index index.html;
    server_name {alt} *.{alt};

    location / {{
        try_files $uri $uri/ @htmlext;
    }}

    location ~ \.html$ {{
        try_files $uri =404;
    }}

    location @htmlext {{
        rewrite ^(.*)$ $1.html last;
    }}
    error_page 404 /404.html;
    location = /404.html {{
            internal;
    }}
    location = /.well-known/wallets/HNS {{
        add_header Cache-Control 'must-revalidate';
        add_header Content-Type text/plain;
    }}
    {ssl}
    }}
    '''
    with open(f'/etc/nginx/sites-enabled/{id}.conf', 'w') as file:
        file.write(conf)

    # Restart nginx
    os.system('systemctl restart nginx')

    # Create certs for ICANN domains
    icann_domains = []
    if is_icann(domain):
        icann_domains.append(domain)
    if 'alt_domains' in site:
        for alt in site['alt_domains']:
            if is_icann(alt):
                icann_domains.append(alt)

    icann_domains = " -d ".join(icann_domains)
    icann_domains = f'-d {icann_domains}'
    os.system(f'certbot --nginx {icann_domains} --non-interactive --agree-tos --email admin@{icann_domains[0]} --redirect')
    return True


def is_icann(domain):
    # Check if domain list is downloaded yet
    if not os.path.isfile('icann.txt'):
        os.system('wget https://data.iana.org/TLD/tlds-alpha-by-domain.txt -O icann.txt')

    tlds = open('icann.txt', 'r').read().split('\n')
    # Remove any comments
    tlds = [tld for tld in tlds if not tld.startswith('#')]
    if domain.split('.')[-1].upper() in tlds:
        return True
    return False