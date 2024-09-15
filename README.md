Ovaj dio opisuje početno postavljanje elasticsearcha, kibane i filebeata korištenjem httpsa.

U direktoriju _Skripte_ se nalaze korištene skripte koje je potrebno postaviti u skrivene sistemske direktorije i osigurati izvršavanje.

Elasticsearch i Kibana se postavljaju na zaseban server, dok se Filebeat postavlja na virtualni stroj Kali Linux.

### Instalacija Elasticsearch-a:
```bash
sudo apt update
sudo apt install elasticsearch
```

### Instalacija Kibane:

```bash
sudo apt install kibana
```

### Instalacija Filebeata:
```bash
sudo apt install filebeat
```

### Omogućavanje SSL-a na Elasticsearchu
### 1. Generiranje SSL certifikata:
Elasticsearch zahtijeva CA (Certificate Authority) za potpisivanje SSL certifikata. Koristite elasticsearch-certutil alat za generiranje:

```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-certutil ca
```
Ovo će generirati ca.zip datoteku koja sadrži potrebne certifikate za CA.

### 2. Generiranje SSL certifikata za Elasticsearch čvorove:

```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-certutil cert --ca ca.zip
````
Ovo će stvoriti certs.zip datoteku koja sadrži certifikate za čvorove.

### 3. Instaliranje certifikata:
Raspakirajte certifikate i kopirajte ih u odgovarajuće direktorije Elasticsearcha:

```bash
unzip certs.zip -d /etc/elasticsearch/cert
```

### 4. Konfiguriranje Elasticsearch-a za korištenje SSL-a:
U Elasticsearch konfiguracijskoj datoteci (/etc/elasticsearch/elasticsearch.yml), dodajte sljedeće postavke kako biste omogućili SSL za HTTP i transportne slojeve:

```yaml
xpack.security.enabled: true

xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: /etc/elasticsearch/certs/elastic-certificates.p12
xpack.security.http.ssl.truststore.path: /etc/elasticsearch/certs/elastic-certificates.p12

xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: /etc/elasticsearch/certs/elastic-certificates.p12
xpack.security.transport.ssl.truststore.path: /etc/elasticsearch/certs/elastic-certificates.p12
````

### 5. Ponovno pokretanje Elasticsearcha:
Nakon izmjene konfiguracijske datoteke, ponovno pokrenite Elasticsearch:

```bash
sudo systemctl restart elasticsearch
````

### Konfiguriranje Kibane za korištenje SSL-a:
U Kibana konfiguracijskoj datoteci (/etc/kibana/kibana.yml), omogućite SSL koristeći iste certifikate kao i za Elasticsearch:

```yaml
server.ssl.enabled: true
server.ssl.certificate: /etc/elasticsearch/certs/elastic-certificates.p12
server.ssl.key: /etc/elasticsearch/certs/elastic-certificates.p12

elasticsearch.ssl.certificateAuthorities: ["/etc/elasticsearch/certs/ca.crt"]

elasticsearch.ssl.verificationMode: certificate

elasticsearch.username: "kibana_system"
elasticsearch.password: "<kibana_lozinka>"
```

### Ponovno pokretanje Kibane:
Nakon izmjene konfiguracije, ponovno pokrenite Kibanu:

```bash
sudo systemctl restart kibana
```
### Konfiguracija Filebeata sa SSL-om

1. Izmjena Filebeat konfiguracije:
U Filebeat konfiguracijskoj datoteci (/etc/filebeat/filebeat.yml), konfigurirajte SSL za komunikaciju s Elasticsearchom:

```yaml
output.elasticsearch:
  hosts: ["https://localhost:9200"]
  ssl.certificate_authorities: ["/etc/elasticsearch/certs/ca.crt"]
  ssl.certificate: "/etc/elasticsearch/certs/elastic-certificates.p12"
  ssl.key: "/etc/elasticsearch/certs/elastic-certificates.p12"
  username: "filebeat_internal_user"
  password: "<filebeat_lozinka>"
````

2. Ponovno pokretanje Filebeata:
Nakon izmjene konfiguracije, ponovno pokrenite Filebeat:

```bash
sudo systemctl restart filebeta
````

Korak 5: Testiranje i Provjera
1. Provjera Elasticsearcha:
Provjerite radi li Elasticsearch s omogućenim SSL-om:

```bash
curl -X GET https://localhost:9200 -u elastic:your_password --cacert /etc/elasticsearch/certs/ca.crt
```

### Provjera Kibane:
Otvorite Kibanu u pregledniku putem https://<vaš-server-ip>:5601 i provjerite funkcionira li SSL.

### Provjera Filebeata:
Provjerite Filebeat logove kako biste osigurali da nema SSL povezanih grešaka:

```bash
sudo tail -f /var/log/filebeat/filebeat.log
```

### Dodatne konfiguracije
Kreiranje internih korisnika:
Koristite Elasticsearch alat za upravljanje korisnicima kako biste kreirali korisnike i uloge za Filebeat i Kibanu:

```bash
curl -X POST "https://localhost:9200/_security/user/filebeat_internal_user" \
     -u elastic:your_password \
     -H "Content-Type: application/json" `
     -d '{ "password" : "your_password", "roles" : [ "filebeat_writer" ] }'
```

### Primjer dijela filebeat.yml konfiguracije 

```yaml
# ============================== Filebeat inputs ===============================

filebeat.inputs:

# Each - is an input. Most options can be set at the input level, so
# you can use different inputs for various configurations.
# Below are the input-specific configurations.
- type: log
  enabled: true
  paths:
    - /home/kali/.command_output_func.log

# ============================== Filestream input ==============================
- type: filestream

  # Unique ID among all inputs, an ID is required.
  id: my-filestream-id

  # Change to true to enable this input configuration.
  enabled: true

  # Paths that should be crawled and fetched. Glob based paths.
  paths:
    - /var/log/*.log
    - /var/log/audit/audit.log
    - /home/kali/.command_log_zsh
```

Kibana se dalje postavlja kroz pregled nadzorne ploče kako bi se pregledavali prikupljeni podaci.
