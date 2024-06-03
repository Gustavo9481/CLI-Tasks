import sqlite3
import os
from typing import List, Dict, Callable, Any
from entities import Task


# ......................... Tareas | módulo database ......................... 󰌠
'''
Servicios de base de datos
Funciones encargadas de las conexiones y consultas a la base de datos
'''

db_path:str = '/home/guscode/Code/Proyectos/P_01_Tareas/Tareas/Proyecto_Tareas.db'
db_connect = sqlite3.connect(db_path)                                     # 🠶 01  

message:str = "Lista de tareas =>"       # contenedor de mensajes de confirmación



# -------------------------------------------------- decorador | gestor_database
def gestor_database(func: Callable[..., Any]) -> Callable[..., Any]:      # 🠶 02
    """
    Decorador para manejar la conexión a la base de datos SQLite y el cursor

    Abre una conexión a la base de datos SQLite,crear un cursor, ejecutar 
    función decorada con el cursor y luego cerrar el cursor
    Maneja cualquier error de la base de datos que pueda ocurrir
    durante la ejecución de la función decorada.

    Args:
        func (Callable): función a decorar. Esta función debe aceptar un 
                         argumento adicional `cursor` que será pasado 
                         automáticamente por eldecorador.

    Returns:
        Callable: La función decorada con manejo automático de 
        la conexión a la base de datos.
    
    Raises:
        sqlite3.Error: Si ocurre un error al acceder a la base de datos.
    """

    def db_decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            with db_connect:
                cursor = db_connect.cursor()
                try:    
                    func(*args, cursor=cursor, **kwargs)
                finally:
                    cursor.close()
        except sqlite3.Error as e:
            print("Ha ocurrido un al acceder a la base de datos")

    return db_decorator



# --------------------------------------------------------- formato de impresión
def format_tasks_list(rows: List) -> None:
    """
    Proporciona el formato a la lista de tareas
    El diccionario caracter determina el color de la etiqueta según el nombre

    Args: 
        rows (list): lista contenedora de resultados de consulta SQL 

    Returns:
        None
    """

    for task in rows:
        caracter:Dict = {
            "urgente":"\x1b[1;31m"+"󰃀"+"\x1b[0m",
            "media":"\x1b[1;33m"+"󰃀"+"\x1b[0m",
            "baja":"\x1b[1;32m"+"󰃀"+"\x1b[0m"
        }
        if task[1] in caracter:
            tag_ico = caracter[task[1]]

        format_list:str = ( 
            f"{task[0]:<5} - {task[1]:<10}{tag_ico}: "
            f"{task[2]:<15}=> {task[3]:<50} {task[4]}"
        )
        print(format_list)



# -------------------------------------------------------- verificar/crear tabla
@gestor_database
def create_table(cursor = None) -> None:
    """
    Verifica si la tabla ya existe, si no existe la crea

    Args:
        cursor: conexión a base de datos sqlite porporcionado por
        el decorador gestor_database
       
    Returns:
        None
    """
    
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS tareas_list (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TAG CHAR(20),
        HASHTAG CHAR(20),
        CONTENT CHAR(300),
        STATUS CHAR(5)
    );
    '''
    cursor.execute(create_table_sql)



# -------------------------------------------------------------- lista de tareas
@gestor_database
def all_tasks(cursor = None) -> None:
    """
    Renderiza la lista completa de tareas. Se ejecuta al iniciar script
    
    Args:
        cursor: conexión a base de datos sqlite porporcionado por
        el decorador gestor_database
       
    Returns:
        None
    """

    cursor.execute(""" SELECT * FROM tareas_list """)
    rows:List = cursor.fetchall()
    format_tasks_list(rows)


    
# ------------------------------------------------------------------ nueva tarea
@gestor_database
def new_task(
        task_tag: str, 
        task_hashtag: str, 
        task_content: str, 
        cursor = None) -> None:
    """
    Crea un nuevo registro en la base de datos (Tarea)
    dependencias: entities.py | Task

    Args:
        tag (str): etiqueta principal de la tarea
        hashtag (str): etiqueta secundario de la tarea
        content (str): contenido o descripción de la tarea
        db_connect (sqlite3.Connection): conexión a base de datos

    Returns
        None
    """
    
    obj_task = Task(tag=task_tag, hashtag=task_hashtag, content=task_content)

    if obj_task:
        cursor.execute(
                "INSERT INTO tareas_list (TAG, HASHTAG, CONTENT, STATUS) "
                "VALUES (?,?,?,?)", 
                (obj_task.tag, obj_task.hashtag, obj_task.content, obj_task.status)
        )



# ----------------------------------------------------- marcar o desmarcar tarea
@gestor_database
def checked_unchecked(task_id: int, cursor = None) -> None:
    """
    Marca o desmarca el status completado/pendiente de la tarea seleccionada

    Args:
        task_id (int): n° id de la tarea que se desea modificar status
        cursor (Any): conexión a la base de datos 

    Returns:
        None
    """
        
    select_task = cursor.execute(
            "SELECT * FROM tareas_list WHERE ID = ?", (task_id,)).fetchone()
    n_status = "󰄲" if select_task[4]=="" else ""
    cursor.execute(
            "UPDATE tareas_list SET STATUS = ? " 
            "WHERE ID = ?", (n_status, task_id)
    )



# --------------------------------------------------------------- filtrar tareas
@gestor_database
def task_filter(required: str, query: str, cursor = None) -> None:
    """
    Filtra las tareas por el tag o hashtag requerido, en el módulo app.py 
    se aplica la condición de la consulta

    Args:
        required (str): tag o hashtag que se desea filtrar
        query (str): consulta SQL
        db_connect (sqlite3.Connection): conexión a base de datos

    Returns:
        None
    """

    filter = cursor.execute(query, (required,))
    rows = cursor.fetchall()
    format_tasks_list(rows)



# ----------------------------------------------------------------- editar tarea
@gestor_database
def edit_task(
        task_id: int, 
        task_tag: str, 
        task_hashtag: str, 
        task_content: str, 
        cursor = None) -> None:
    """
    Edita los campos de las tareas, excepto el status

    Args:
        task_id (int): n° id de la tarea a editar 
        task_tag (str): nuevo tag para la tarea 
        task_hashtag (str): nuevo hashtag para la tarea
        task_content (str): nuevo contenido de la tarea
        db_connect (sqlite3.Connection): conexión a base de datos

    Returns:
        None
    """

    data: List = [task_tag, task_hashtag, task_content]
    
    select_task = cursor.execute(
            "SELECT * FROM tareas_list WHERE ID = ?", 
            (task_id,)).fetchone()
    cursor.execute(
            "UPDATE tareas_list SET TAG = ?, HASHTAG = ?, CONTENT = ? " 
            "WHERE ID = ?", (*data, task_id))

 

# --------------------------------------------------------------- eliminar tarea
@gestor_database
def delete_task(task_id: int, cursor = None) -> None:
    """
    Elimina el registro de tarea de la base de datos

    Args:
        task_id (int): Número de tarea (id de data base)
        db_connect (sqlite3.Connection): Conexión a base de datos
    
    Returns:
        None
    """

    cursor.execute("DELETE FROM tareas_list WHERE ID = ?", (task_id,))
    

