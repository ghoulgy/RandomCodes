import logging, sys
from flask import Flask, make_response, abort
app = Flask(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# From any route (wildcard all)
@app.route('/<path:url_path>', methods=['POST', 'GET'])
def dummmy_universal_server(url_path):
    
    # if Something found in the file path
    # return 404
    if "Something" in url_path:
        abort(404)
    
    # Open Files that will pass back to the client as response
    path = './ImNewbie.dll'
    data_file = open(path,'rb')
    contents = data_file.read()
    data_file.close()

    logging.info(f'From path: /{url_path}')

    # Header's data
    # headers = {"Content-Type": "text/html"}

    # Send back the response to the client
    return make_response(
        contents,
        200,
        # headers=headers
    )

@app.errorhandler(404)
def not_found():
    # Page not found
    return make_response(
        "IM DEAZ",
        404
    )

# Game starts!
if __name__ == '__main__':
    app.run()
