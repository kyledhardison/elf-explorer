
## Installation
The following programs are required:
* docker
* python3/pip3

Run the following command to install pip dependencies:
* `pip3 install pip install dash-bootstrap-components dash networkx plotly graphviz`

## Running
* Disassassemble a binary of your choice using ddisasm (several `.gtirb` examples have been provided as well)
    * `docker run -it -v $(pwd):/work/ grammatech/ddisasm bash -c "cd /work/; ddisasm <file>.o --ir <file>.gtirb"`
    * For efficiency, a smaller binary is recommended.
* Run ELF Explorer, passing the disassembled gtirb file as an argument:
    * `python3 elf-explorer.py samples/printf/printf.gtirb`
* Access ELF Explorer in your browser at http://127.0.0.1:8050/

### Sources
C database sourced from https://www.ibm.com/docs/en/i/7.3?topic=extensions-standard-c-library-functions-table-by-name

dash/plotly reference: https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7

### Future Work
* A hierarchical custom graph algorithm would be nice, that makes main the obvious central route
* Legend for node colors
* Function labeling/grouping - details from GTIRB auxdata
* Auto-resizing for larger binaries
