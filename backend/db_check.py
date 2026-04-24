from app import create_app
from app.models import db

def check_database():
    app = create_app()

    with app.app_context():
        try:
            inspector = db.inspect(db.engine)

            tables = inspector.get_table_names()

            if tables:
                print("Tablas existentes:")
                for table in tables:
                    print("-", table)
            else:
                print("No hay tablas en la base de datos.")

        except Exception as e:
            print("Error al conectar con la base de datos:")
            print(e)


if __name__ == "__main__":
    check_database()