from flask import Flask
app = Flask(__name__)

@app.route('/<rgb_color>')
def hello_world(rgb_color):
    rgb = [eval(rgb_color[0:3]), eval(rgb_color[3:6]), eval(rgb_color[6:])]
    print rgb
    return rgb_color + " was set."

if __name__ == '__main__':
    app.run()