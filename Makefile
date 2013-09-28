default:
	@echo "usage: make sample-family.png"

%.png: %.txt
	./familytreeparser.py $^ > /tmp/family.dot
	dot -Tpng -o $@ /tmp/family.dot
