# Digital Inclusion Dashboard

NYS Digital Inclusion Dashboard Project

Database IP: 34.133.250.109
Project Deployment: http://52.255.175.216


To run this app you need a .env file with the following variables:

```
MYSQL_HOSTNAME = " . . . "
MYSQL_USER = " . . . "
MYSQL_PASSWORD = " . . . "
MYSQL_DATABASE = " . . . "
```

## Installation

To run this app on a cloud server, you need to do the following:

1. Deploy a VM instance on GCP, Azure, AWS, ETC.
    - Make sure to open port 80 and 443
    - Note: This app was designed to run on Ubuntu 
2. VM Instance Setup:
    - Perform a `sudo apt-get update`
    - Install Python3 and pip3 with `sudo apt-get install python3 python3-pip`
    - Note: Sometimes (especially on Azure) you may need to add /home/{username}/.local/bin to your PATH variable and to sudoers file
        - For PATH: `export PATH=/home/username/.local/bin:$PATH`
        - For sudoers: `sudo visudo` and add `/home/{username}/.local/bin:` to the beginning of the line that starts with `Defaults secure_path`
            - Example: `Defaults secure_path="/home/{username}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"`
3. Clone this repo into the VM instance
    - Perform a `git clone {repo_url}`
4. Install the required packages
    - Perform a `pip3 install -r requirements.txt`
5. Create a .env file with the required variables
    - See the .env.example file for an example
6. Run the app
    - Perform a `sudo streamlit run Digital_Inclusion_Dashboard.py --server.port 80`

## Usage Tutorial

Once you've successfully launched the streamlit on either localhost or on a Virtual machine feel free to [How-Tos](https://github.com/israelmiller/digital_inclusion_dashboard/tree/main/How-Tos) to know how to navigate/utilize the dashboard.  
