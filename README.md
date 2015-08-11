# TransitSurveyor API

**author:** Jeffrey Meyers (jeffrey.alan.meyers@gmail.com)

Copyright © 2015 Jeffrey Meyers. This program is released under the "MIT License". Please see the file COPYING in the source distribution of this software for license terms.

Here are instructions for how to get a server/database up and running for the [API](https://github.com/TransitSurveyor/API) to receive and store data collected using [MobileSurveyor](https://github.com/TransitSurveyor/MobileSurveyor).

+ *OS:* Ubuntu 14.04
+ *Database:* PostgreSQL 9.3
+ *Framework:* Python/Flask
+ *Server:* NginX/uWSGI

#### Create a (virtual private) server
If needed signup with [DigitalOcean](https://www.digitalocean.com/), then create a droplet. This will cost you $5 dollar a month to run. You can take a snapshot then destroy to avoid being charged when not using it. [Tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-your-first-digitalocean-droplet-virtual-server)
+ choose Ubuntu 14.04 with 512MB RAM

#### Build and Configure

I mostly followed [THIS](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04) tutorial to workout how to deploy the Flask app with NginX and uWSGI.

```shell
# connect to your new VPS server
# DigitalOcean will email you the one-time root password if you do not include an ssh keys
ssh root@new_ip_address

# create new user
useradd -d /home/survey -s /bin/bash -m survey
passwd survey # enter new password for `survey` user

# if you change the user from `survey` to something else
# you need to make that change in `setup.sh` also

# download and execute setup script
curl https://raw.githubusercontent.com/TransitSurveyor/API/master/setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh new_ip_address

start api               #   expected output: api start/running, process XXXXXX
service nginx restart   #   expected output: * Restarting nginx nginx

```

#### run tests

A basic suite of tests to make sure endpoints are working and database is configured properly

```shell
su - survey
cd API
env/bin/python tests.py
```

#### default settings
+ **linux user:** *survey*
+ **linux user pw:** whatever you entered when running `passwd survey`
+ **postgres db name:** *survey*
+ **postgres db user:** *survey*
+ **postgres db user pw:** *survey*

#### new config and startup script file locations
+ **Flask app configuration:** `/home/survey/API/config.py`
+ **uWSGI startup config:** `/home/survey/API/api.ini`
+ **uWSGI upstart init script:** `/etc/init/api.conf`
+ **uWSGI wsgi script:** `/home/survey/API/wsgi.py`
+ **NginX server config:** `/etc/nginx/sites-available/api`

In addition to these files, there is a new environment variable `API_ENDPOINT` added to **survey** user's `~/.bashrc` that allows the unit tests to access the live endpoint.


## Description

Data is received as either a SCAN or STOP. SCAN records occur when collection is done using the **QR Code Scanner** mode while STOP records occur when collection is done using the **Map-Based** mode.

##### SCAN

A scan received consists of the following data

- unique identifier from QR code
- route
- direction
- surveyor id
- timestamp
- mode (ON or OFF)
- latitude and longitude of scan

Based on *mode* the data is handled differently. For **ON** records the data is inserted into a temporary table. Handling **OFF** records requires a few more steps.

1. Query temporary table looking for unmatched ON scan by comparing unique identifier, route and direction.
2. If no match is found nothing happens. The temporary table gets cleared during downtime.
3. If a match is found
    - The record in the temporary table is flagged to avoid future matches
    - A spatial lookup is done using the lat-lon coordinates for the nearest bus stop for given route and direction
    - New ON-OFF record is saved

##### STOP

A stop received consists of the data below. Lookups are done in a stops table to find the corresponding keys
for boarding and alighting stops and then all the data is written to a postgres database.

- route
- direction
- surveyor id
- timestamp
- boarding stop ID
- alighting stop ID
