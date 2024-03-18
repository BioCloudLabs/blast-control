import os
import json
import ansible_runner

def run():

    hosts = {
        'hosts': {
            'mi_vm': {
                'ansible_host': '168.63.124.223',
                'ansible_user': 'tu_usuario_ssh',
                'ansible_password': 'tu_contraseña_ssh'
            }
        }
    }

    # Define el playbook de Ansible para instalar Docker
    playbook = {
        'hosts': 'mi_vm',  # El nombre del host que definiste en el inventario
        'gather_facts': False,
        'tasks': [
            {
                'name': 'Install Docker',
                'become': True,
                'apt': {  # Esta tarea instala Docker en sistemas basados en Debian (Ubuntu)
                    'name': 'docker.io',
                    'update_cache': True
                }
            }
        ]
    }

    # Configura los argumentos para Ansible Runner
    kwargs = {
        'playbook': [playbook],
        'inventory': {'all': hosts}
    }

    # Ejecuta el playbook con Ansible Runner
    result = ansible_runner.run(**kwargs)

    # Imprime los resultados
    print("Estado de la ejecución:")
    print(json.dumps(result.stats, indent=4))
    print("Salida estándar:")
    print(result.stdout)

run()
