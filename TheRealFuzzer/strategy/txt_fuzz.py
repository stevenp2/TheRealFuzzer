from .csv_fuzz import CSV_Fuzzer

class TXT_Fuzzzer():
    # Takes in CSV_Fuzzer to use its strategies as well
    def __init__(self, Runner, content):
        # self.csv_fuzzer = CSV_Fuzzer(Runner, content)
        self.runner = Runner
        self.content = content

    def strategies(self):
        return CSV_Fuzzer(self.runner, self.content).strategies_txt()