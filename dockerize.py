import paramiko

def install_docker(server_ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server_ip, username=username, password=password)

        # Update the apt package index and install packages to allow apt to use a repository over HTTPS
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt update')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # Install docker.io
        # _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))

        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        print(f'Docker on {server_ip} was installed successfully.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ssh.close()

def copy_ssh_key(server_ip, username, password, key_path="/home/christiangoac/.ssh/id_rsa.pub"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server_ip, username=username, password=password)

        # Read the public key file
        with open(key_path, "r") as key_file:
            public_key = key_file.read()

        # Add the public key to the authorized_keys file on the remote server
        _, stdout, stderr = ssh.exec_command(f'echo "{public_key}" >> ~/.ssh/authorized_keys')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        print(f'Public key copied to {server_ip} successfully.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ssh.close()

def run_blast(server_ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server_ip, username=username, password=password)

        # Clone blast repo
        # _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive git clone https://github.com/BioCloudLabs/blast.git')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))

        # _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt install apache2 -y')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))

        # Start docker container
        # _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive docker-compose -f blast/docker-compose.yaml up --build')
        # print(stdout.read().decode('utf-8'))
        # print(stderr.read().decode('utf-8'))

        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive docker run -d -p 80:80 nginx')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        print(f'Docker container {server_ip} it\'s now running.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        ssh.close()

def setup_and_run(server_ip, username, password):
    copy_ssh_key(server_ip, username, password)
    install_docker(server_ip, username, password)
    run_blast(server_ip, username, password)
