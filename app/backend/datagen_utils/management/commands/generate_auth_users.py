from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from authentification.models import AuthUser, Persona
from faker import Faker # Changed from datagen_utils
import random
import datetime
from django.db import transaction

class Command(BaseCommand):
    help = 'Genera usuarios falsos utilizando AuthUser y Persona'

    def add_arguments(self, parser):
        parser.add_argument('--cantidad', type=int, default=1000,
                            help='Cantidad de usuarios a generar (default: 1000)')
        parser.add_argument('--batch', type=int, default=500,
                            help='Tamaño del lote para inserciones (default: 500)')

    def handle(self, *args, **kwargs):
        cantidad = kwargs['cantidad']
        batch_size = kwargs['batch']
        
        fake = Faker('es_ES')  # Usamos locale español
        
        # Listas para nombres y apellidos (más rápido que Faker para cada uno)
        nombres_ejemplo = ["Ana", "Luis", "Carlos", "Maria", "Juan", "Laura", "Sofia", "Diego", "Valeria", "Martin"]
        apellidos_ejemplo = ["García", "Martinez", "Lopez", "Rodriguez", "Perez", "Gomez", "Sanchez", "Diaz", "Alvarez", "Romero"]

        # Valores por defecto para campos simplificados
        fecha_nacimiento_default = datetime.date(1990, 1, 1)
        direccion_default = "Calle Falsa 123"
        telefono_default = "555-0100"

        # Tipos de usuario disponibles según el modelo
        tipos_usuario = ['doctor', 'paciente', 'administrativo']
        
        # Especialidades médicas para doctores
        especialidades = [
            'Cardiología', 'Dermatología', 'Endocrinología', 
            'Gastroenterología', 'Ginecología', 'Neurología',
            'Oftalmología', 'Oncología', 'Pediatría',
            'Psiquiatría', 'Traumatología', 'Urología'
        ]
        
        # Consultorios para doctores
        consultorios = [f'Consultorio {i}' for i in range(1, 11)]
        
        auth_users = []
        personas = []
        total_created_count = 0 # Initialize total count
        
        self.stdout.write(f'Generando {cantidad} usuarios falsos...')
        
        # Usamos transacción para mejorar el rendimiento y garantizar consistencia
        with transaction.atomic():
            for i in range(cantidad):
                # username = fake.unique.user_name() # Comentado
                username = f"usuario_{i+1}" # Simplificado: usa el índice del bucle
                
                # password = make_password(fake.password(length=12)) # Comentado para prueba de velocidad
                password = "testpassword123" # Simplificado: contraseña estática en texto plano
                
                # Crear AuthUser
                auth_user = AuthUser(
                    username=username,
                    password=password
                )
                auth_users.append(auth_user)
                
                # Si alcanzamos el tamaño del lote, insertar AuthUsers
                if len(auth_users) >= batch_size or i == cantidad - 1:
                    AuthUser.objects.bulk_create(auth_users)
                    total_created_count += len(auth_users) # Increment total count
                    self.stdout.write(f'Insertados {len(auth_users)} AuthUsers... Total creados hasta ahora: {total_created_count}')
                    
                    # Crear Personas para los AuthUsers creados
                    for user in auth_users:
                        tipo_usuario = random.choice(tipos_usuario)
                        
                        # Datos específicos según el tipo de usuario
                        if tipo_usuario == 'doctor':
                            especialidad = random.choice(especialidades)
                            consultorio = random.choice(consultorios)
                        else:
                            especialidad = None
                            consultorio = None
                        
                        # Generar fecha de nacimiento (entre 18 y 80 años atrás)
                        # fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=80) # Comentado
                        
                        persona = Persona(
                            auth_user=user,
                            tipo_usuario=tipo_usuario,
                            nombre=random.choice(nombres_ejemplo), # Simplificado
                            apellido=random.choice(apellidos_ejemplo), # Simplificado
                            fecha_nacimiento=fecha_nacimiento_default, # Simplificado
                            direccion=direccion_default, # Simplificado
                            telefono=telefono_default, # Simplificado
                            especialidad=especialidad,
                            consultorio=consultorio
                        )
                        personas.append(persona)
                    
                    # Insertar todas las personas
                    Persona.objects.bulk_create(personas)
                    self.stdout.write(f'Insertadas {len(personas)} Personas...')
                    
                    # Limpiar listas para el próximo lote
                    auth_users = []
                    personas = []
        
        self.stdout.write(self.style.SUCCESS(f'¡{total_created_count} usuarios creados exitosamente!'))
