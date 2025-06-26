from interface import Interface
import sys
import khess
import json
import traceback

''' this script is used ran from a subprocess inside SurgePlayer
    This is done so we can run the engine in pypy3 '''

def process(interface, command):
    """Process incoming json commands"""
    try:
        data = json.loads(command)
        method = "exec"
        args = data.get("args", [])

        if hasattr(interface, method):
            result = getattr(interface, method)(*args)
            print(json.dumps({"result": result[0], "explanation": result[1]}))  # Send response
            sys.stdout.flush()
        else:
            print(json.dumps({"error": "not found method"}))  # Send response
            sys.stdout.flush()
    except Exception as e:
        # handle error message
        error_message = traceback.format_exc()
        print(json.dumps({"error": error_message}), file=sys.stderr)
        sys.stderr.flush()



if __name__ == "__main__":
    ''' This is what will be run from the main code '''
    # create an instance of interface - to communicate with engine
    interface = Interface(think=khess.find_best_move)
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        process(interface, line)

