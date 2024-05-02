import paramiko

def install_docker(server_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pkey = paramiko.RSAKey.from_private_key_file("/home/christiangoac/.ssh/id_rsa")
        ssh.connect(server_ip, username="azure", pkey=pkey, look_for_keys=False)

        # Update the apt package index and install packages to allow apt to use a repository over HTTPS
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt update')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # Install docker.io
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        
        print(f'Docker on {server_ip} was installed successfully.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ssh.close()

def run_blast(server_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pkey = paramiko.RSAKey.from_private_key_file("/home/christiangoac/.ssh/id_rsa")
        ssh.connect(server_ip, username="azure", pkey=pkey, look_for_keys=False)

        # Clone blast repo
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive git clone https://github.com/BioCloudLabs/blast.git')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # _, stdout, stderr = ssh.exec_command(f'sudo DEBIAN_FRONTEND=noninteractive scp /home/christiangoac/biocloudlabs.cer azure@{server_ip}:/home/azure/biocloudlabs.cer')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))

        # _, stdout, stderr = ssh.exec_command(f'sudo DEBIAN_FRONTEND=noninteractive scp /home/christiangoac/biocloudlabs.key azure@{server_ip}:/home/azure/biocloudlabs.key')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))


        # Start docker container
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive SERVER_NAME=blast-2.biocloudlabs.es docker-compose -f blast/docker-compose.yml up --build')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        print(f'Docker container {server_ip} it\'s now running.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ssh.close()

def setup_and_run(server_ip):
    install_docker(server_ip)
    run_blast(server_ip)