import subprocess

def get_upstream(branch_name):
    try:
        command = ["git", "rev-parse", "--abbrev-ref", branch_name + "@{u}"]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return output.decode("ASCII").strip(" \n")
    except subprocess.CalledProcessError:
        return None