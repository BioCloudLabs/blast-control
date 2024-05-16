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
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io cifs-utils')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        
        return {"message": f'Docker on {server_ip} was installed successfully.'}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        ssh.close()

def run_blast(server_ip, server_name):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pkey = paramiko.RSAKey.from_private_key_file("/home/christiangoac/.ssh/id_rsa")
        ssh.connect(server_ip, username="azure", pkey=pkey, look_for_keys=False)

        # Clone blast repo
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive docker pull biocloudlabs/blast:latest')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # Build docker image
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive mkdir results/ queries/ blastdb/')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # Start docker container in detached mode
        _, stdout, stderr = ssh.exec_command('sudo chmod -R 777 results/ queries/ blastdb/')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        # Start docker container in detached mode
        _, stdout, stderr = ssh.exec_command('sudo DEBIAN_FRONTEND=noninteractive mount -t cifs -o guest,vers=3 //blastdb.biocloudlabs.es/blastdb blastdb/')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        _, stdout, stderr = ssh.exec_command(f'sudo DEBIAN_FRONTEND=noninteractive docker run -p 443:443 -e SERVER_NAME={server_name} -v /home/azure/queries:/var/www/app/queries -v /home/azure/results:/var/www/app/results -v /home/azure/blastdb:/var/www/app/blastdb -v /var/run/docker.sock:/var/run/docker.sock -v /home/azure:/etc/ssl/certs -v /home/azure:/etc/ssl/private --privileged biocloudlabs/blast:latest &')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

        return {"message": f'Docker container {server_ip} it\'s now running.'}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        ssh.close()

def setup_and_run(server_ip, server_name):
    install_docker_output = install_docker(server_ip)
    if "error" in install_docker_output:
        return install_docker_output
    return run_blast(server_ip, server_name)