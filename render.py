

def site_list(sites):
    html = ''
    for site in sites:
        html += f'<tr><td><a href="/manage/{site["name"]}">{site["name"]}</a></td><td>{site["domain"]}</td><td>{site["active"]}</td></tr>'
    return html


def alt_domains(domains):
    if len(domains) == 0:
        return "No alternate domains"

    html = '<ul>'
    for domain in domains:
        html += f'<li>{domain}</li>'
    html += '</ul>'
    return html

def site_content(site,files):
    # <li class="list-group-item"><span>List Group Item 1</span></li>
    html = ''
    for file in files:
        html += f'<li class="list-group-item"><span>{file}</span> | <a href="/manage/{site}/download/{file}">Download</a> | <a href="/manage/{site}/delete/{file}">Delete</a></li>'
    return html

def dns_info(info):
    html = ''
    for domain in info:
        html += f'<tr><td>{domain["domain"]}</td><td>{domain["ip"]}</td><td>{domain["tlsa"]}</td></tr>'
    return html