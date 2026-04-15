import sys
from sqlalchemy import inspect
from backend.app import create_app, db

def check_database():
    print("--- Verificando conexión a la Base de Datos ---")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Intentar conectar
            # El engine se obtiene de la instancia de db vinculada a la app
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"Estado: [OK] Conexión establecida exitosamente.")
            print(f"URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # 2. Verificar existencia de tablas
            if tables:
                print(f"Tablas encontradas ({len(tables)}): {', '.join(tables)}")
                
                required_tables = ['cities', 'places']
                missing = [t for t in required_tables if t not in tables]
                
                if not missing:
                    print("Resultado: [VÁLIDO] Todos los modelos base están presentes.")
                else:
                    print(f"Resultado: [INCOMPLETO] Faltan las tablas: {', '.join(missing)}")
            else:
                print("Resultado: [ADVERTENCIA] Conexión exitosa, pero la base de datos está vacía.")
                print("Tip: Asegúrate de que db.create_all() se ejecutó correctamente.")

        except Exception as e:
            print(f"Estado: [ERROR] No se pudo conectar a la base de datos.")
            print(f"Detalle: {str(e)}")
            print("\n--- Guía de solución de problemas ---")
            print("1. ¿Está corriendo PostgreSQL localmente?")
            print("2. ¿El archivo .env existe y tiene el DATABASE_URL correcto?")
            print("3. ¿El usuario 'admin' tiene permisos sobre la base de datos 'citylens'?")
            sys.exit(1)

if __name__ == "__main__":
    check_database()