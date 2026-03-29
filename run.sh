#!/bin/bash

echo "=============================="
echo "   Hadoop WordCount Project   "
echo "=============================="

# Default input file (can override)
INPUT_FILE=${1:-input/input.txt}

echo "Using input file: $INPUT_FILE"

echo "Cleaning old files..."
rm -rf output
rm -f src/*.class
rm -f jar/wordcount.jar

echo "Compiling Java..."
javac -classpath `hadoop classpath` src/WordCount.java

echo "Creating JAR..."
jar -cvf jar/wordcount.jar -C src/ . > /dev/null

echo "Running Hadoop job..."
hadoop jar jar/wordcount.jar WordCount $INPUT_FILE output

echo ""
echo "===== Raw Output ====="
cat output/part-r-00000

echo ""
echo "===== Sorted Output (Top 5 Words) ====="
cat output/part-r-00000 | sort -k2 -nr | head -n 5
