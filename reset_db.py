from sqlalchemy import text

from app import create_app, db

app = create_app()

with app.app_context():
    db.session.execute(text("DROP SCHEMA public CASCADE"))
    db.session.execute(text("CREATE SCHEMA public"))
    db.session.commit()

    print("Schema public reiniciado completamente")