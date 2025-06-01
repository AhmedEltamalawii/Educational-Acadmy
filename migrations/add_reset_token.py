from pythonic import app, db

def add_reset_token_column():
    with app.app_context():
        # Add reset_token column to User table
        db.engine.execute('ALTER TABLE user ADD COLUMN reset_token VARCHAR(100) UNIQUE')
        print("Added reset_token column to User table")

if __name__ == "__main__":
    add_reset_token_column() 