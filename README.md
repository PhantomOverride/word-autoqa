# word-autoqa

word-autoqa is a simple python3 script that checks if the text in a Word document passes or fails some rules. Rules are simple regular expressions, and the text fails if they match. An explaination is printed for any rule that triggers a fail.

The intention is to check for common mistakes and blunders automatically.

## Usage

~~~
$ qa test.docx
[ + ] Running validation rules against file test.docx
 [ ! ] Contains an example. ("A random example!" from pattern "[Aa].[Rr]andom.[eE]xample!") [ 1 ] 
[ + ] Finished. 1 rules passed, 1 failed.
~~~

Flag `-c` can be used to suppress colour output.
Flag `-p` will print pass messages as well as fail messages.

## Rules

Rules are stored in the `rules` directory. The script will load and merge rules from all files in this directory, and then run them against the target files. This means that rules in the rule folder may be split into multiple files; the script will use all files.

To add a new rule, simply append it to one of the files, or create a new file.

The `find` attribute contains a regular expression that will be passed to `re.findall`. The rules are case sensitive, but insensitivity can be set for the rule with the `(?i)` modifier (e.g. `(?i)example` will match "ExAmPlE").
