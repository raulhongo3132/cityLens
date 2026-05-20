from sqlalchemy import text

from app import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()

    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()

    print("Base de datos reiniciada completamente")