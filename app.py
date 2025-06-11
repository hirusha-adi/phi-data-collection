from flask import Flask
import pocketbase

app = Flask(__name__)

pb = pocketbase.PocketBase("http://127.0.0.1:8090")
super_user = pb.admins.auth_with_password("app@example.com", "12345678")


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
