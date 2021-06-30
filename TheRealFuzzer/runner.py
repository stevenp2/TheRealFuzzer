import subprocess

class Runner:
    def __init__(self, binary, text):
        self.binary = binary
        self.text = text

    def run_process(self, inp=""):
        """Run the binary with `inp` as input.  Return result of `subprocess.run()`."""
        return subprocess.run(self.binary,
                              input=inp,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def run(self, inp=""):
        """Run the binary with `inp` as input.  Return test outcome based on result of `subprocess.run()`."""
        result = self.run_process(inp)

        if result.returncode == 0:
            outcome = self.PASS
        elif result.returncode < 0:
            outcome = self.FAIL
        else:
            outcome = self.UNRESOLVED

        return (result, outcome)