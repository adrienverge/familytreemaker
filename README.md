familytreemaker
===============

This program creates family tree graphs from simple text files.

The input file format is very simple, you describe persons of your family line
by line, children just have to follow parents in the file. Persons can be
repeated as long as they keep the same name or id. An example is given in the
file `LouisXIVfamily.txt`.


Installation
------------

Simply clone the repo.

This script outputs a graph descriptor in DOT format. To make the image
containing the graph, you will need a graph drawer such as [GraphViz] [1].

[1]: http://www.graphviz.org/  "GraphViz"

Usage
-----

The sample family descriptor `LouisXIVfamily.txt` is here to show you the
usage. Simply run:
```
$ ./familytreemaker.py -a 'Louis XIV' LouisXIVfamily.txt | dot -Tpng -o LouisXIVfamily.png
```
It will generate the tree from the infos in `LouisXIVfamily.txt`, starting from
*Louis XIV* and saving the image in `LouisXIVfamily.png`.

You can see the result:

![result: LouisXIVfamily.png](/LouisXIVfamily.png)
