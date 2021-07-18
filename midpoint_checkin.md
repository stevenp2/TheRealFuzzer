# Fuzzer Midpoint Checkin

## Requirements:
```
sudo apt install qemu-user
```


# Fuzzer Description:
## How the Fuzzer Works
### A general overview

```
                                                            +------------------+
                                                            |   bad_stuff.py   |
                                                            +--+--+--+--+------+
                                                               |  |  |  |
                                                               |  |  |  |
                                                            +--v---------------+
                                                    +------>|  csv_fuzz.py     +
                                                   /        +------------------+\
                                                  /               |  |  |        \
                                                 /          +-----v------------+  \
                                                /+--------->|  json_fuzz.py    +   \
                                               //           +------------------+\   \
                                              //                     |  |        \   \
  +-----------------+    +------------------+//             +--------v---------+  \   \                    +----------------+
  |  fuzzer.py      +---->   checker.py     ++------------->|  xml_fuzz.py     +---+---+------------------>|   runner.py    |
  +-----------------+    +------------------+\              +------------------+  /                        +----------------+
                                              \                         |        /
                                               \            +-----------v------+/
                                                +---------->|  txt_fuzz.py     +
                                                            +------------------+

                                                            +------------------+
                                                            |  mutation.py     +
                                                            +------------------+
```

- `fuzzer.py` contains the main logic which takes in a binary and an input
- `checker.py` checks for file type and the architecture of the binary
- then based off the file type, `_*fuzz.py` will apply the fuzzing technique
- *bad_stuff.py* contains some bad integers and strings which is inserted into some of the strategies utilised by the type_fuzzers
- `runner.py` calls qemu-[architecture] and runs the binary against the payload produced by `*_fuzz.py` (it also spits out a log_report file of syscalls which later will be in use)
- `mutation.py` has not been implemented yet and as such it is not called

### Some more detail
In the beginning, the `fuzzer.py` takes in a `binary_input` and `input.txt`. Since we are told `input.txt` will be a valid form, it reamins to check what file type it is. The funcion `check_type` in `checker.py` :

```py
def check_type(text):
	with open(text, 'r') as f:
		if _is_json(f):
			return 'json'
		elif _is_xml(f):
			return 'xml'
		elif _is_csv(f):
			return 'csv'
		elif _is_txt(f):
			return 'txt'
```
is ordered in such a way as the csv check used (for some reason) treated a json as a csv file. Moreover, the strategies for csv and txt files overlap to some extent because of this.

In order to see what type of architecture the binary uses, `checker.py` also has a function
```py
def check_arch(input_file):
    p = subprocess.check_output(['file', f'{input_file}'])
    result = str(p)
    if 'Intel 80386' in result:
        return 'i386'
    elif 'x86-64' in result:
        return 'x86_64'
```
This is important later on as knowing the architecture allows qemu to be called which serves to allow for log generation.

After this checks are finished (the architecture and filetype is set), a `*_fuzzer.py` takes over and generates payloads which are dependent on the filetype.

So far the fuzzer uses elementary checks such as format strings, integer overflows, integer underflows, buffer overflows, etc. The checks vary as the format has to be taken into account in order to get the most coverage. 

For example, consider a `binary` that handles json and a `json.txt` like the following:
```
{
	'cost': 10,
	'customers': 0 
}
```
If the `binary` was very specific such that it only took in 'cost' as the key like such:
```py
cost = json_txt['cost'] # 10

important_function(cost) # <--- will break if it is not int
```
then changing the key would have no effect at all.

In the case of the strategies `json_fuzz.py`, the key-value pairs of `json.txt`  would consider cases where the key is not mutated (only mutating the value) e.g. mutating it to something like

```
{
	'cost': -2**8+1,
	'customers': 🐒 
}
```
Only after a certain number of iterations of this it begins to change the key value and then apply further strategies.

Within all the `*_fuzz.py` strategies, `runner.py` is called which handles commandline calls by inserting a the generated payload into the binary file. Originally, what occured in `runner.py` was:
```py
import pwn

with process(binary) as p:
	p.send(payload)

	exit_status = p.returncode

	p.close()
```
However, this ran into some deadlock issues within the pwntools library because of the rate at which the payloads were being generated. Moreover, using this was extremely slow and was seen as an overhead.

As a result, the next strategy was to turn to calling subprocesses in the following manner:
```py
import subprocess

with subprocess.Popen(binary,
					  stdin=subprocess.PIPE,
					  stdout=subprocess.DEVNULL,
					  stderr=subprocess.DEVNULL) as p:

	payload = p.communicate(payload)

	exit_status = p.returncode
```
This reduced the overhead caused from the previous code by a lot and there wasn't anymore issues with a deadlock anymore. 

The next problem was log generation and coverage. After reading up on greybox fuzzers and their strategies, it was deemed useful to somehow have some sort of logging in order to perform a kind of measure on how well the payload did in the run. This was also considered as fuzzing the `jpg1.txt` would be hard. After searching for a few days on the internet for a solution on how to generate coverage logs of subprocesses, there was no solid solution (most solutions required having the source file).

As a result, the subprocess method was entirely ditched and qemu-system was used as this actually generated some logs which could form the basis for coverage.

## Improvements to be made
This fuzzer is planned to have two stages:
- basic fuzzing - generated simple input from the `*_fuzz.py` files
- converage fuzzing - fuzz based off how well the input covers the program

Already right now, the basic fuzzing method is rather slow due to some overheads which could likely be fixed by using more cores with the multiprocessing library. This has yet to be implemented (mostly due to lack of experience with using multiprocessing library).

In regards to the basic fuzzing, there are still some strategies that have not yet been implemented and cases to be covered such as considering keywords, though, the main focus the towards converage fuzzing.

There remains a lot of improvement to be made to the coverage fuzzing.
One includes actually managing and figuring out what to do something with the `./log_report/log` which is generated each time a process is run using qemu. Moreover, the `./log_report/log` is generated each time a process is run which can be seen as an overhead as a file is continously being written to. Attempts have been made to try and store the data within that file inside some list, but there has not been much progress.

The fuzzer also has not implemented any displays not detection of infinite loops.

##  Something Awesome 
If the coverage is successful then technically a grey box fuzzer is implemented. Perhaps this could be seen as a some extra added feature 👀