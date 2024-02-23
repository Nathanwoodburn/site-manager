from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import datetime
import json
import render
import account
import sites as sites_module

app = Flask(__name__)
dotenv.load_dotenv()


#Assets routes
@app.route('/assets/<path:path>')
def send_report(path):
    return send_from_directory('templates/assets', path)


@app.route('/sitemap')
@app.route('/sitemap.xml')
def sitemap():
    # Remove all .html from sitemap
    with open('templates/sitemap.xml') as file:
        sitemap = file.read()

    sitemap = sitemap.replace('.html', '')
    return make_response(sitemap, 200, {'Content-Type': 'application/xml'})

@app.route('/favicon.png')
def faviconPNG():
    return send_from_directory('templates/assets/img', 'favicon.png')


# Main routes
@app.route('/')
def index():
    cookie = request.cookies.get('session')
    if not cookie:
        return redirect('/login')
    user = account.check_cookie(cookie)
    if not user:
        return redirect('/login')           

    site_info = sites_module.get_info()
    sites = sites_module.load_sites()
    active_sites = site_info['active_sites']
    total_sites = site_info['total_sites']  
    site_list = render.site_list(sites)
    
    return render_template('index.html', user=user, year=datetime.datetime.now().year, sites_active=active_sites, sites_total=total_sites, site_list=site_list)

@app.route('/create', methods=['POST'])
def create_site():
    data = request.form
    name = data['name']
    domain = data['domain']
    sites_module.add_site(name, domain)
    return redirect('/')

@app.route('/manage/<name>')
def manage_site(name):
    cookie = request.cookies.get('session')
    if not cookie:
        return redirect('/login')
    user = account.check_cookie(cookie)
    if not user:
        return redirect('/login')           

    site = sites_module.get_site(name)
    if not site:
        return render_template('404.html', year=datetime.datetime.now().year), 404
    
    alt_domains = []
    if 'alt_domains' in site:
        alt_domains = site['alt_domains']
    
    alt_domains = render.alt_domains(alt_domains)
    checked = 'checked' if site['active'] else ''

    files = sites_module.get_content(name)
    files = render.site_content(name, files)

    dns_info = sites_module.get_dns_info(name)
    dns_info = render.dns_info(dns_info)

    return render_template('manage.html', user=user, year=datetime.datetime.now().year,
                           site=site['name'], domain=site['domain'], enabled=site['active'],
                           alt_domains=alt_domains, checked=checked, files=files, dns_info=dns_info)


@app.route('/manage/<name>/alt', methods=['POST'])
def add_alt_domain(name):
    data = request.form
    domain = data['domain']
    site = sites_module.get_site(name)
    if not site:
        return render_template('404.html', year=datetime.datetime.now().year), 404

    
    sites_module.add_alt_domain(name, domain)
    return redirect(f'/manage/{name}')


@app.route('/manage/<name>/enable', methods=['POST'])
def enable_site(name):
    enable = request.form.get('enable')
    sites_module.enable(name, enable)
    return redirect('/manage/' + name)

@app.route('/manage/<name>/upload', methods=['POST'])
def upload_site(name):
    site = sites_module.get_site(name)
    if not site:
        return "Error: Site not found."

    file = request.files['file']
    if not file:
        return "Error: No file provided."

    if file:
        if not os.path.isdir('/var/www/{id}'.format(id=site['id'])):
            os.mkdir('/var/www/{id}'.format(id=site['id']))

        filename = file.filename
        file.save('/var/www/{id}/{filename}'.format(id=site['id'], filename=filename))
        # If .zip file, extract it to /var/www/{id}
        if filename.endswith('.zip'):
            os.system('unzip /var/www/{id}/{filename} -d /var/www/{id}'.format(id=site['id'], filename=filename))
            os.remove('/var/www/{id}/{filename}'.format(id=site['id'], filename=filename))
            # If all files are in a folder, move them to /var/www/{id}
            files = os.listdir('/var/www/{id}'.format(id=site['id']))
            if len(files) == 1 and os.path.isdir('/var/www/{id}/{file}'.format(id=site['id'], file=files[0])):
                os.system('mv /var/www/{id}/{file}/* /var/www/{id}'.format(id=site['id'], file=files[0]))
                os.system('rm -rf /var/www/{id}/{file}'.format(id=site['id'], file=files[0]))
                        
    return "File uploaded successfully."

@app.route('/manage/<name>/download/<file>')
def download_site(name, file):
    site = sites_module.get_site(name)
    if not site:
        return "Error: Site not found."
    
    if os.path.isfile('/var/www/{id}/{file}'.format(id=site['id'], file=file)):
        return send_from_directory('/var/www/{id}'.format(id=site['id']), file, as_attachment=True)
    
    # if file is a directory, zip it and send it
    if os.path.isdir('/var/www/{id}/{file}'.format(id=site['id'], file=file)):
        os.system('cd /var/www/{id} && zip -r {file}.zip {file}'.format(id=site['id'], file=file))
        return send_from_directory('/var/www/{id}'.format(id=site['id']), file + '.zip', as_attachment=True)
    

@app.route('/manage/<name>/delete/<file>')
def delete_site(name, file):
    site = sites_module.get_site(name)
    if not site:
        return "Error: Site not found."
    
    # If file is a directory, remove it recursively
    if os.path.isdir('/var/www/{id}/{file}'.format(id=site['id'], file=file)):
        os.system('rm -rf /var/www/{id}/{file}'.format(id=site['id'], file=file))
    else:
        os.remove('/var/www/{id}/{file}'.format(id=site['id'], file=file))    
    return redirect('/manage/' + name)











@app.route('/<path:path>')
def catch_all(path):
    year = datetime.datetime.now().year
    # If file exists, load it
    if os.path.isfile('templates/' + path):
        return render_template(path, year=year)
    
    # Try with .html
    if os.path.isfile('templates/' + path + '.html'):
        return render_template(path + '.html', year=year)

    return render_template('404.html', year=year), 404


@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = data['username']
    password = data['password']

    if account.login(user, password):
        cookie = account.generate_cookie(user)
        response = make_response(redirect('/'))
        response.set_cookie('session', cookie, max_age=60*60*24*30)
        return response

    return jsonify({'error': 'Invalid credentials'}), 401

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', year=datetime.datetime.now().year), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')