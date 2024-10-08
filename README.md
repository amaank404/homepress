## V2 in progress, check it out [here](https://github.com/amaank404/homepress/tree/pymupdf) 

# Homepress

Converts your documents (PDF) into a directly printable pdf that has pages
ordered in such a manner that the resultant print can be binded at the middle page.
This mimics how some books are printed.

# Functionalities and Usage Instructions

Homepress comes with different types of binding methods. 

## midpage

![](images/midpage_binding.png)

here the sheets are printed on the half side of the whole sheet and the printed stack is folded from the middle and binded there. This works for a stack at most 10-20 pages thick. Binding is done manually using stapler or thread.

command for this becomes:

```
homepress {InputFile} midpage [printing_options] {OutputFile}
```

## midpage multistack

![](images/midpage_multi_stack.png)

it is similar to midpage binding. The difference being that the input document is divided into multiple sub documents that are processed just like midpage binding. Then the multiple stacks that are produced can be binded together via special threading techniques or glue like shown below.

![](images/multistack_binding.png)

command for this becomes:

```
homepress {InputFile} midpage-multi [printing_options] {OutputFile} 
```

# Printing Options

in the above binding methods, `[printing_options]` should be replaced by a space separated sequence of the following flags if you want to.

## `-ss` / `--single-sided`
Just dont, please, just don't use this, it breaks most of the other print options, you are much better off never using this.

## `-rtl` / `--right-to-left`
By default, this is set to false. for certain languages like arabic and certain print formats like japanese mangas require the pages to be printed right to left. this format does exactly that. The printed stack is to be opened from right to left.

## `-f` / `--flip-even`

This options flips the even pages on the horizontal axis, using this depends on your printer. If your printer supports double sided printing, please turn this on, without this, the printing would be a mess and the output would be wasted. For a single sided printer, leave this as is.

For single sided printers, first print the odd pages of the output and then input the output in exact same manner but flip the printed stack horizontally. Then, print the even pages of the output pdf. This will give you a stack that you must first ensure is in order and then you can fold it from the middle.

## `-s` / `--separate-even-odd`

Separates the even and odd pages of the output into two different pdf files. Use this if your printing mechanism doesn't support choosing to print only odd/even pages. For this case, you must provide the output paramater with two file names. First one for odd pages pdf and the second one for even pages pdf

## `-ipr` / `--input-page-range`

For programmer use only, see the --help documentation for usage.

## `-ss`/ `--stack-size`

For multi-stack binding, this sets the size of an individual stack. The stack size is not guarenteed, it might have 1 more page than expected to eliminate last small stack. Stack size must be a multiple of 4 because 4 pages per physical sheet (double sided) is printed. I recommend leaving this somewhere between 32 and 48.

## `-sst` / `-separate-stacks`

For multi-stack binding, by default false, the stacks are separated into files into the output folder going by the names "stack_1.pdf", "stack_2.pdf", etc...

## `-q` / `--quite`

When set to true, no progress report is shown. by default, the process reports the progress to the terminal.
