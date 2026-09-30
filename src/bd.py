from .claves.config import bd
import psycopg

def guardar_usuario(id_usr: int):
    """Guarda el id_usr en la BD si no se encuentra registrado previamente."""
    if not id_usr:
        return
    sql_insert = """
    INSERT INTO usrs_tg (id_usr)
    VALUES (%s)
    ON CONFLICT (id_usr) DO NOTHING;
    """
    try:
        with psycopg.connect(bd) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_insert, (id_usr,))
                conn.commit()
    except Exception as e:
        print(f"Error al guardar el usuario {id_usr} en la BD:", e)
