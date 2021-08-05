# elf, jpeg, plaintext covered here

class Mutation_Fuzzer():
    def __init__(self, Runner, content):
        self.runner = Runner
        self.content = content

    def initiate():
        pass

    # idea -> find the type of file we are working with e.g. json
    #      -> have certain "smart fuzzing" functions and go through each of them
    #      -> rank them based off coverage
    #      -> and then do some fuzzing on it and see if they generate any more code paths