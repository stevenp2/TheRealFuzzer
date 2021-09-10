# TheRealFuzzer

## Requirements:
```
sudo apt install qemu-user
pip3 install matplotlib
```
## Run:
```
./fuzzer.py [location_of_binary] [location_of_input]
```

# Assumptions
- All binaries will have a vulnerability.
- All binaries will function normally (return 0, not crash, no errors) when the relevant input.txt is passed into them.
- All binaries will expect input in one of the following formats:
    - Sub Plaintext (multiline)
    - JSON
    - XML
    - CSV
    - JPEG
    - ELF
    - PDF
- The input. txt provided will be a valid form of one of these text formats.
- All binaries will be 32 bit linux ELF's (except xml3).
- All vulnerabilities will result in memory corruption.

# Fuzzer Description:
## How the Fuzzer Works
### A general overview

```
                                                                    +---------------+
                                                                    | bad_stuff.py  +----------------------+
                                                                    +-+--+--+--+--+-+                      |
                                                                      |  |  |  |  |                        |
                                                                      |  |  |  |  |                        |
                                                                    +-v-------------+                      |
                     +---------------+                        +-----> csv_fuzz.py   +------+       +-------v--------+
        +------------>  reporter.py  +-----------+            |     +---------------+      |       |  mutation.py   +-------------------+
        |            +---------------+           |            |          |  |  |  |        |       +-------^--------+                   |
        |                                        |            |     +----v----------+      |               |                            |
        |                                        |            +-----> json_fuzz.py  +------|               0                            |
+-------+-------+    +---------------+           |            |     +---------------+      |               |                     +------v---------+
|  fuzzer.py    +---->  checker.py   +-----------+------------+             |  |  |        +---------------+---1---------------->    runner.py    |
+---------------+    +---------------+                        |     +-------v-------+      |                                     +----------------+
                                                              +-----> xml_fuzz.py   +------|
                                                              |     +---------------+      |
                                                              |                |  |        |
                                                              |     +----------v----+      |
                                                              +-----> txt_fuzz.py   +------|
                                                              |     +---------------+      |
                                                              |                   |        |
                                                              |     +-------------v-+      |
                                                              +-----> jpg_fuzz.py   +------+
                                                                    +---------------+
```

- `fuzzer.py` contains the main logic which takes in a binary and an input
- `reporter.py` attaches to the majority of the `*.py` files and prints to stdout and appends to log_report/log of what has occured for trouble shooting
- `checker.py` checks for file type and the architecture of the binary
- `_*fuzz.py` will apply the fuzzing technique based off the file type given by `checker.py`
- `mutation.py` is where the coverage based fuzzing occurs if `_*fuzz.py` fails to produce a `bad.txt` file
- `bad_stuff.py` contains some bad integers and strings which is inserted into some of the strategies utilised by the `_*fuzz.py` and `mutation.py`
- `runner.py` calls qemu-[architecture] and runs the binary against the payload produced by `*_fuzz.py` (it will spit out log files when running the fuzzing under `mutation.py`)

### Some more detail
In the beginning, the `fuzzer.py` takes in a `binary_input` and `input.txt`. Since we are told `input.txt` will be a valid form, it remains to check what file type it is. The funcion `check_type` in `checker.py` will do exactly that as it will also give the archicture the binary uses which is important for later on when basic fuzzing fails and the program needs to apply coverage based mutation fuzzing.

After the checks are finished (the architecture and filetype is set), a `*_fuzzer.py` takes over and generates payloads which are dependent on the filetype as valid input should be generated which can then be parsed. Which ever `*_fuzzer.py` is used is then logged into log_report/log which provides information how many iterations it took to find a `bad.txt`, which technique found the bad payload, and under which fuzzer.

If the `*_fuzzer.py` fails to produce results, the program then moves towards the mutation based coverage method in `mutation.py`. The `mutation.py` fuzzer works by firstly generating a log file `tmp/program_exec`, by calling the function `run_process_coverage` in `runner.py` on the initial input.txt file given. The file contains all the unchained executions that `qemu-[system]` translated, which is then proccessed into a dictionary containing important functions such as main, vuln, etc. and their associated addresses where they have been executed. For example, a processed log file for a very small program will produce something like:

```py
    {
        main: [0x08040000, 0x00804200, 0x08040220],
        vuln: [0x08084030, 0x08040035],
        parse: [0x0804015]
    }
```
The measure, then, that the coverage uses is the total number of unique executions at different addresses of the important functions that `qemu-[system]` processed (in the above example, it would be 6). On the idea of visiting a dead end in terms of execution, the fuzzer has been iterated over 100 times for each binary (which could seg fault as a result of mutation) to determine the average of how many times the same number of total execution appears would mean a dead end. So, for example, after 16 executions with 86 total unique executions appearing in each one, the fuzzer will assume that it has reached a dead end. This average (painstakingly) calculated is 16.498.

Once `mutation.py` has been successful, in determining a `bad.txt`, it will also generate a graph `log_report/function_coverage.png` via matplotlib showing the 'distance' of the payload from the input.txt file i.e. how many extra executions occured to lead to a segmentation fault.

Moreover, when the fuzzer is about to complete, a graph `log_report/return_code.png` is also generated which shows the number of different crashes/return codes that have occured.

# Mutation Methods:
## General Method
Methods performed are dependent on the file type, however, the are general methods that have been applied such that the input.txt file remains valid whilst the mutation has occured. These include:
- bitflips
- byteflips
- int negation
- int replacement with out of bound ints
- file expansion
    - This includes injected repeated parts of elements from the input file. For example, in `xml_fuzz`, the `shuffle_elements` strategy adds multiple parts of the input file into the payload
    - `json_fuzz`, `txt_fuzz`, and `csv_fuzz` also do something similar to the above
- replacements
    - Byte replacements - this is more specific towards jpg_fuzz where the bytes (excluding SOI AND EOI) are replaced with some random `magic_numbers` from `bad_stuff.py`
    - Value replacement - in json inputs, the value of some key may be replaced with another json input which could eventually become nested
    - Site replacement - for xml inputs, if a site is found, then that site will be intelligently replaced/mutated so that it contains both valid and invalid urls

## Converage Based
As explained under `How the fuzzer works`, the method uses the input.txt file as a base for perform the total number of unchained executions translated by `qemu-[system]`. The coverage works by using that base number as comparison to eventually form a payload with a higher number of total executions than the base. That new payload then becomes the base and the cycle continues. If it is determined that the fuzzer has reached a dead end, the total number of executions is added to a blacklist and payloads reach that total number of executions, the new payload does not change and remains the same to ensure a different path is executed.
For example, suppose that the base number of total executions is 45, then the fuzzer would do something like below:
```
iteration 1
45 --> 45 --> 65 --> 65 --> 65 --> 65 --> 79 --> 90 --> 90 --> (repeats 16 times)

*resetting*

iteration 2
45 --> 65 --> 79 -?-> 90 (but 90 is a deadend)
                  |    
                  `--> 85 --> 86 --> ...
```
The coveraged based mutation method is also mutations intelligently in the sense that it will aim to mutate the payload such that it is valid every time. 

# Logging:
Under `/log_report`, there will be 3 files upon a successful fuzzing. The 3 files are:
- log
    - Contains information about which fuzzer was used, the strategy, and after how many iterations a payload was found under that strategy (if any was found)
- function_coverage.png
    - If `mutation.py` is called and is successful in finding a payload, then will be produced which function_coverage.png graphs the number of executions that was needed to find the payload in comparison to the inital input.txt file   
- return_code.png
    - Near the end off the program, a return_code.png will be produced which graphs the types of crashes that have occured with the payloads 

There will also be a `tmp` file containing program_exec file which will be the last iteration of the input binary which led seg fault (assuming a `bad.txt` is produced). There is also asome logging to stdout.

# Improvements to be made
Whilst many overheads have been removed, the fuzzer is still *extremely* slow as a result of calling `qemu-[system] -d exec,nochain -D /tmp/program_exec ...` every time to perform coverage based fuzzing. This is a result of the log being generated every single time and qemu set to not produce and TB (translated blocks). This was done in such as way as it was the most effective to get a verbose log in order to perform coverage based fuzzing. On the other hand, the problem with doing so is that the function prologue is called everytime which extends the time taken to get the more important functions by increasing the length of the log.

An idea was to somehow set a hook at the `_start` function so the log file generated would not be as large  (in memory resetting) but there was not enough time and resources to find out how to do this. Moreover, another thought was to do what AFL does and fork a server, however, this was not possible due to unfamiliarity with threading (as a result, the program runs on a single thread which makes it pretty slow).

The program was planned to fix some overheads by introducing multiprocessing, however, there was not enough time to implement this as the focus was more towards making a decent coverage based fuzzer.  

In regards to the logs generated being very large, a consequence of that is sometimes `jpg1` will not work under coverage based fuzzing and will just be killed by the terminal. Again, this would be fixed by doing in memory resetting.

Since the fuzzer was not able to find a seg fault under `jpg`, perhaps, there is a technique for fuzzing `jpg` files that was not listed. Also, the fuzzer cannot fuzz ELF and PDF files yet. This was due to a lack of time and focus towards getting the coverage based fuzzing to work. 

Also 3/4 way into the making of this fuzzer, there was some regret relating to using python as it is harder to control memory which made the attempts at trying coverage based fuzzing and in memory resetting even longer as it was kind of hard finding a solution. Although, in the end the coverage based fuzzing was somewhat complete.

##  Something Awesome 
The coverage based fuzzing in `mutation.py` is somewhat successfully implemented, but there remains more keywords to add to `bad_stuff.py` and file type techniques that could be implemented to further solidify it. As stated previously, `mutation.py` currently only mutations the file.txt by changing elements in it and doesn't expand the file yet.  

A good way to test that it works is by going to `csv_fuzz.py` and comment out the strategies like so:
```py
class CSV_Fuzzer():
    def __init__(self, Runner, content, reporter):
        self.runner = Runner
        self.content = content
        self.reporter = reporter

        self.reporter.set_fuzzer('CSV Fuzzer')
        self.reporter.send_to_stdout('CSV file detected - applying CSV Fuzzer')
        

    def strategies(self):
        self.reporter.send_to_stdout('Applying CSV strategies now')
        time.sleep(0.5)
        return [
            # self.negate_everything(),
            # self.vary_delimiters(),
            # self.expand_file(),
            # self.oob_ints(),
            # self.bit_flip(),
        ]
```
Then run: 

```
python3 fuzzer.py ../testfiles/csv2 ../testfiles/csv2.txt
```
It also works for `json1`, `plaintext1`, and other that don't require any extra elements be added.

