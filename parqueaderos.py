import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parámetros del modelo
tiempos_servicio = {
    'Rápido': 1,
    'Normal': 3,
    'Lento': 4,
    'Muy Lento': 6
}

tasas_llegada = {
    'Rápido': 1/3,
    'Normal': 1/3,
    'Lento': 1/5,
    'Muy Lento': 1/7
}

proporciones = {
    'Rápido': 0.25,
    'Normal': 0.20,
    'Lento': 0.30,
    'Muy Lento': 0.25
}

# Función para determinar el tipo de usuario basado en las proporciones
def tipo_usuario():
    rand = np.random.rand()
    if rand < proporciones['Rápido']:
        return 'Rápido'
    elif rand < proporciones['Rápido'] + proporciones['Normal']:
        return 'Normal'
    elif rand < proporciones['Rápido'] + proporciones['Normal'] + proporciones['Lento']:
        return 'Lento'
    else:
        return 'Muy Lento'

# Proceso de atención del cajero
def atencion_cajero(env, cajero, datos):
    while True:
        usuario = tipo_usuario()
        tiempo_servicio = np.random.exponential(tiempos_servicio[usuario])
        yield env.timeout(tiempo_servicio)
        datos.append((usuario, tiempo_servicio))  # Guardar el tipo de usuario y el tiempo de servicio

# Proceso de simulación principal
def simulacion(env, num_cajeros, datos):
    cajeros = [simpy.Resource(env) for _ in range(num_cajeros)]
    while True:
        usuario = tipo_usuario()
        tiempo_llegada = np.random.exponential(1 / tasas_llegada[usuario])
        yield env.timeout(tiempo_llegada)
        
        # Asignar el usuario a un cajero disponible
        with np.random.choice(cajeros).request() as request:
            yield request
            env.process(atencion_cajero(env, request, datos))

# Ejecutar la simulación
def ejecutar_simulacion(num_cajeros, tiempo_simulacion):
    env = simpy.Environment()
    datos = []  # Crear la lista de datos aquí
    env.process(simulacion(env, num_cajeros, datos))
    env.run(until=tiempo_simulacion)
    return datos

# Graficar resultados
def graficar_resultados(datos_transitorios, datos_estables):
    df_transitorio = pd.DataFrame(datos_transitorios, columns=['Tipo_Usuario', 'Tiempo_Servicio'])
    df_estable = pd.DataFrame(datos_estables, columns=['Tipo_Usuario', 'Tiempo_Servicio'])

    # Calcular tiempos promedio por tipo de usuario
    tiempos_promedio_transitorio = df_transitorio.groupby('Tipo_Usuario')['Tiempo_Servicio'].mean().sort_index()
    tiempos_promedio_estable = df_estable.groupby('Tipo_Usuario')['Tiempo_Servicio'].mean().sort_index()

    # Crear el gráfico de barras agrupadas
    bar_width = 0.35
    indices = np.arange(len(tiempos_promedio_transitorio))
    
    plt.figure(figsize=(12, 7))
    
    plt.bar(indices - bar_width/2, tiempos_promedio_transitorio, bar_width, label='Estado Transitorio', color='skyblue')
    plt.bar(indices + bar_width/2, tiempos_promedio_estable, bar_width, label='Estado Estable', color='salmon')
    
    plt.title('Comparación de Tiempos Promedio de Servicio')
    plt.xlabel('Tipo de Usuario')
    plt.ylabel('Tiempo Promedio de Servicio (minutos)')
    plt.xticks(indices, tiempos_promedio_transitorio.index)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    print("Tiempos Promedio de Servicio (Estado Transitorio):")
    for tipo_usuario, tiempo_promedio in tiempos_promedio_transitorio.items():
        print(f'{tipo_usuario}: {tiempo_promedio:.2f} minutos')

    print("\nTiempos Promedio de Servicio (Estado Estable):")
    for tipo_usuario, tiempo_promedio in tiempos_promedio_estable.items():
        print(f'{tipo_usuario}: {tiempo_promedio:.2f} minutos')

    # Calcular el cajero con menor y mayor tiempo promedio de atención
    tiempo_promedio_min_transitorio = tiempos_promedio_transitorio.min()
    tiempo_promedio_max_transitorio = tiempos_promedio_transitorio.max()
    cajero_min_transitorio = tiempos_promedio_transitorio.idxmin()
    cajero_max_transitorio = tiempos_promedio_transitorio.idxmax()

    tiempo_promedio_min_estable = tiempos_promedio_estable.min()
    tiempo_promedio_max_estable = tiempos_promedio_estable.max()
    cajero_min_estable = tiempos_promedio_estable.idxmin()
    cajero_max_estable = tiempos_promedio_estable.idxmax()

    print(f'\nEstado Transitorio:')
    print(f'Cajero con menor tiempo promedio de atención: {cajero_min_transitorio} con {tiempo_promedio_min_transitorio:.2f} minutos')
    print(f'Cajero con mayor tiempo promedio de atención: {cajero_max_transitorio} con {tiempo_promedio_max_transitorio:.2f} minutos')

    print(f'\nEstado Estable:')
    print(f'Cajero con menor tiempo promedio de atención: {cajero_min_estable} con {tiempo_promedio_min_estable:.2f} minutos')
    print(f'Cajero con mayor tiempo promedio de atención: {cajero_max_estable} con {tiempo_promedio_max_estable:.2f} minutos')

# Análisis y recomendaciones
def analizar_resultados(datos):
    # Calcular el promedio de usuarios de cada tipo en la totalidad de cajeros
    conteo_usuarios = {'Rápido': 0, 'Normal': 0, 'Lento': 0, 'Muy Lento': 0}
    for usuario, _ in datos:
        conteo_usuarios[usuario] += 1
    
    total_usuarios = sum(conteo_usuarios.values())
    promedio_conteo_usuarios = {usuario: conteo / total_usuarios for usuario, conteo in conteo_usuarios.items()}
    
    print("\nProporciones Promedio de Cada Tipo de Usuario:")
    for tipo_usuario, promedio_conteo in promedio_conteo_usuarios.items():
        print(f'{tipo_usuario}: {promedio_conteo:.2f}')

    # Recomendaciones basadas en los resultados
    tiempos_servicio_promedio = {usuario: np.mean([tiempo for u, tiempo in datos if u == usuario]) for usuario in conteo_usuarios}
    
    print("\nTiempos Promedio de Servicio Después de Filtrar Transitorios:")
    for tipo_usuario, tiempo_promedio in tiempos_servicio_promedio.items():
        print(f'{tipo_usuario}: {tiempo_promedio:.2f} minutos')

    if tiempos_servicio_promedio['Lento'] > 4 or tiempos_servicio_promedio['Muy Lento'] > 6:
        print("\nRecomendación: Considerar agregar más cajeros para mejorar el tiempo de atención.")
    else:
        print("\nRecomendación: El número actual de cajeros parece ser suficiente.")

# Ejecutar simulación y graficar resultados
num_cajeros = 3
tiempo_simulacion = 100 # Tiempo total de simulación en minutos

# Simulación con estado transitorio
datos_transitorios = ejecutar_simulacion(num_cajeros, tiempo_simulacion)

# Eliminar el estado transitorio (repetir simulación para más datos)
datos_estables = ejecutar_simulacion(num_cajeros, tiempo_simulacion)

# Graficar resultados después de eliminar el estado transitorio
graficar_resultados(datos_transitorios, datos_estables)

# Análisis de resultados
analizar_resultados(datos_transitorios)
