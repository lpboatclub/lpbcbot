1. Create `pyuser` and add to sudoers group
    
    sudo adduser pyuser
    sudo usermod -a -G sudo pyuser
    
2. Create `/opt/python` directory and take ownership
```bash
    sudo mkdir -p /opt/python
    sudo chown pyuser python
```
3. Download lpbcbot project

    `git clone https://github.com/mikeblum/lpbcbot.git`

4. Configure virtualenv
 
    `virtualenv . && source ./bin/activate`

5. Install system dependencies

    sudo apt-get install libxml2-dev libxslt1-dev python-dev	

6. Pull down Python libraries
	
    pip install -r ./requirements.txt

7. Crete ENV variables file `setenv.sh`:

```bash
    #!/bin/bash
    export OPEN_WEATHER_TOKEN=
    export TWITTER_CONSUMER_KEY=
    export TWITTER_CONSUMER_SECRET=
    export TWITTER_ACCESS_TOKEN=
    export TWITTER_ACCESS_TOKEN_SECRET=
```

8. Run script manually:

    . ./setenv.sh && python main.py
