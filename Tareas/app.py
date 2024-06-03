import os
import subprocess                                                          
import sqlite3
from functools import partial
from database import (
        db_connect, new_task, delete_task, create_table,
        checked_unchecked, edit_task, task_filter, 
        all_tasks, gestor_database, message 
)


# ..................... Tareas | lista to-do en cónsola ...................... 󰌠
'''
Aplicación simple de tareas, lista to.do en cónsola con las funciones de:
    - Crear nuevas tareas, asignando tag y hastag
    - Marcar y desmarcar tareas como completadas o pendientes 
    - Filtrar tareas por tag, hashtag o status
    - Editar tareas ya existentes
    - Eliminar tareas
    - Base de datos SQLite para datos persistentes
'''



def main(message: str) -> None:
    """
    Función ejecutora del script, contiene las funciones principales
    dependencias: database.py & entities.py | *

    Args:
        message (str): contenedor de mensajes de confirmación

    Returns:
        None
    """


    # ......................................... limpiar pantalla
    def clear_screen() -> None:
        """
        Ejecuta comando -clear- en la terminal 
        dependencia: módulo subprocess | run()

        Returns:
            None
        """

        clear_comand: List = ["clear"]
        subprocess.run(clear_comand)                                      # 🠶 01 



    # .............................................. nueva tarea 
    def menu_new_task(db_connect: sqlite3.Connection, message: str) -> None:
        """
        Crea una nueva tarea, solicitando los datos necesarios al usuario, como:
        - tag:      etiqueta de identificación de la tarea
        - hashtag:  sub etiqueta de identificación de la tarea
        - content:  contenido de la tarea
        dependencia: módulo database.py | new_task(), message

        Args:
            db_connect (sqlite3.Connection): conexión a base de datos sqlite
            message (str): contenedor de mensajes de confirmación | database.py

        Returns:
            None
        """

        tag: str = input("ingrese etiqueta => [ baja - media - urgente]: ")
        hashtag: str = input("ingrese el hastag: ")
        content: str = input("contenido de la tarea: ")
     
        new_task(tag, hashtag, content)
        clear_screen()
        message = "La tarea ha sido creada..."

        main(message)        
    


    # ................................. marcar o desmarcar tarea
    def menu_checked_unchecked(db_connect: sqlite3.Connection, message: str) -> None:
        """
        Cambia el status de las tareas, pendiente => completado y viceversa
        mostrando un mensaje de corfirmación del cambio
        dependencia: módulo database.py | checked_unchecked(), message

        Args:
            db_connect (sqlite3.Connection): conexión a base de datos sqlite
            message (str): contenedor de mensajes de confirmación | database.py

        Returns:
            None
        """

        id: int = input("n° de tarea a cambiar status: ")
        checked_unchecked(id)

        clear_screen()
        message = f"Se modificó el status de la tarea N°: {id}"

        main(message)



    # ........................................... filtrar tareas
    def menu_task_filter(db_connect: sqlite3.Connection, message: str) -> None:
        """
        Filtra tareas por tag o hashtag. Dicha opción se solicitará al usuario
        Muestra mensaje de confirmación del filtro utilizado
        dependencia: módulo database.py | task_filter(), message

        Args:
            db_connect (sqlite3.Connection): conexión a base de datos sqlite
            message (str): contenedor de mensajes de confirmación | database.py

        Returns:
            None
        """

        query_tag: str = (
                "SELECT ID, TAG, HASHTAG, CONTENT, STATUS " 
                "FROM tareas_list " 
                "WHERE TAG = ?"
        )
        
        query_hashtag: str = (
                "SELECT ID, TAG, HASHTAG, CONTENT, STATUS " 
                "FROM tareas_list " 
                "WHERE HASHTAG = ?"
        )
        
        gum_query: List = ["gum", "choose", "tag", "hashtag"]
        
        query_select = subprocess.run(gum_query, stdout=subprocess.PIPE, text=True)
        select_query = query_select.stdout.strip()

        if select_query == "tag":                                         # 🠶 02  
            required = input("ingrese el tag: ")
            query = query_tag
            task_filter(required, query)
            message = f"\nTareas filtradas por: \x1b[1;31m{required}\x1b[0m\n"

        elif select_query == "hashtag": 
            required = input("ingrese el hashtag: ")
            query = query_hashtag
            task_filter(required, query)
            message = f"\nTareas filtradas por: \x1b[1;31m{required}\x1b[0m\n"

        else:
            pass



    # ............................................. editar tarea 
    def menu_edit_task(db_connect: sqlite3.Connection, message: str) -> None:
        """
        Solicita el n° de tarea y edita los datos de la misma, suministrados
        por el usuario
        dependencia: módulo database.py | edit_task(), message

        Args:
            db_connect (sqlite3.Connection): conexión a base de datos sqlite
            message (str): contenedor de mensajes de confirmación | database.py

        Returns:
            None
        """
        
        print("editar tarea =>")
        id: int = input("n° de tarea a editar: ")
        tag: str = input("nueva etiqueta: ")
        hashtag: str = input("nuevo hastag: ")
        content: str = input("nuevo contenido de la tarea: ")
        edit_task(id, tag, hashtag, content)

        clear_screen()
        message = f"Tarea n° {id} ha sido editada"

        main(message)



    # ........................................... eliminar tarea
    def menu_delete_task(db_connect: sqlite3.Connection, message: str) -> None:
        """
        Elimina la tarea indicada por id
        dependencia: módulo database.py | delete_task(), message
        
        Args:
            db_connect (sqlite3.Connection): conexión a base de datos sqlite
            message (str): contenedor de mensajes de confirmación | database.py

        Returns:
            None
        """
        
        id: int = input("n° id de tarea a eliminar: ")
        delete_task(id)
        clear_screen()
        message = f"Se eliminó la tarea N°: {id}"

        main(message)

 

    # ............................. start execution .............................. 󰌠
    
    create_table()

    title_command: List = [ "gum", "style",
	"--foreground", "'#9dff00'", "--border-foreground", "'#9dff00'", "--border", "double",
	"--align", "center", "--width", "90", "--margin", "'2 1'", "--padding", "'0.5 4'", 
	"CLI-Tasks | Gestor de tareas TO-DO 󰄲 "]
    
    subprocess.run(title_command, text=True)

    print(f"\n \x1b[1;31m{message}\x1b[0m\n")                             # 🠶 03  

    all_tasks()
   
    comand_gum = [
        "gum", 
        "choose", 
        "nueva tarea", 
        "marcar o desmarcar tarea",
        "filtrar tareas",
        "editar tarea",
        "eliminar tarea", 
        "salir",
        "--cursor=  ",
        "--selected.foreground='212'"
    ]
    
    print("\n")
    captura = subprocess.run(comand_gum, stdout=subprocess.PIPE, text=True)
    selection = captura.stdout.strip()
    
    menu_options: Dict = {
        "nueva tarea": partial(menu_new_task, db_connect, message),       # 🠶 04 
        "marcar o desmarcar tarea": partial(menu_checked_unchecked, db_connect, message),
        "filtrar tareas": partial(menu_task_filter, db_connect, message),
        "editar tarea": partial(menu_edit_task, db_connect, message),
        "eliminar tarea": partial(menu_delete_task, db_connect, message),
    }
   
    if selection in menu_options:
        menu_options[selection]()
    else:
        exit()

    


if __name__ == "__main__":
    
    main(message)
