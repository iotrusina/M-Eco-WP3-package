/***	accent_main.cc	***/

/*	Copyright (C) Jan Daciuk, 1996-2004	*/

/*

This program looks for words from standard input, and tries to find
morphological information for that words in speficied dictionaries.

Synopsis:
fsa_accent options

options are:
[-d dictionary]...
-a accent_file

where dictionary is a file containing the dictionary in a form of a binary
automaton. At least one dictionay must be specified.
Accent file contains relations between the accented characters, and their latin
equivalents.

Words are read from standard input, and results written to standard
output.

*/

#include	<iostream>
#include	<fstream>
#include	<string.h>
#include	<stdlib.h>
#include	<new>
#include	<unistd.h>
#include	"fsa.h"
#include	"nstr.h"
#include	"common.h"
#include	"accent.h"
#include	"fsa_version.h"

static const int	Buf_len = 256;	// Buffer length for accent file
static const int	MAX_LINE_LEN = 512;	// Buffer length for input

using namespace std;

int
main(const int argc, const char *argv[]);
int
usage(const char *prog_name);
void
not_enough_memory(void);
accent_tabs *
make_accents_table(const char *file_name);




/* Name:	not_enough_memory
 * Class:	None.
 * Purpose:	Inform the user that there is not enough memory to continue
 *		and finish the program.
 * Parameters:	None.
 * Returns:	Nothing.
 * Remarks:	None.
 */
void
not_enough_memory(void)
{
  cerr << "Not enough memory for the automaton\n";
  exit(4);
}//not_enough_memory

/* Name:	main
 * Class:	None.
 * Purpose:	Launches the program.
 * Parameters:	argc		- (i) number of program arguments;
 *		argv		- (i) program arguments;
 * Returns:	Program exit code:
 *		0	- OK;
 *		1	- invalid options;
 *		2	- dictionary file could not be opened;
 *		4	- not enough memory;
 *		5	- accent file non-existant or cannot be used.
 * Remarks:	None.
 */
int
main(const int argc, const char *argv[])
{
  word_list	dict;		// dictionary file name 
  int		arg_index;	// current argument number
  const char	*accent_file_name = NULL;// relations between characters
  accent_tabs	*accents;	// accent equivalence table
  word_list	inputs;		// names of input files (if any)
  const char 	*lang_file = NULL; // name of file with character set

  set_new_handler(&not_enough_memory);

  for (arg_index = 1; arg_index < argc; arg_index++) {
    if (argv[arg_index][0] != '-')
      // not an option
      return usage(argv[0]);
    if (argv[arg_index][1] == 'd') {
      // dictionary file name
      if (++arg_index >= argc)
	return usage(argv[0]);
      dict.insert(argv[arg_index]);
    }
    else if (argv[arg_index][1] == 'a') {
      // file that contains relations between accented characters and their
      // latin equivalents
      if (++arg_index >= argc)
	return usage(argv[0]);
      accent_file_name = argv[arg_index];
    }
    else if (argv[arg_index][1] == 'i') {
      // input file name
      if (++arg_index >= argc)
	return usage(argv[0]);
      inputs.insert(argv[arg_index]);
    }
    else if (argv[arg_index][1] == 'l') {
      // language file name
      if (++arg_index >= argc)
	return usage(argv[0]);
      lang_file = argv[arg_index];
    }
    else if (argv[arg_index][1] == 'v') {
#include "compile_options.h"
      return 0;
    }
    else {
      cerr << argv[0] << ": unrecognized option\n";
      return usage(argv[0]);
    }
  }//for

  if (accent_file_name == NULL) {
    cerr << "Accent file name not specified\n";
    return usage(argv[0]);
  }

  if (dict.how_many() == 0) {
    cerr << argv[0] << ": at least one dictionary file must be specified\n";
    return usage(argv[0]);
  }

  if ((accents = make_accents_table(accent_file_name)) == NULL)
    // could not make accent table (message already printed in funtion)
    return 5;

  accent_fsa fsa_dict(&dict, lang_file);
  if (!fsa_dict) {
    if (inputs.how_many()) {
      inputs.reset();
      do {
	ifstream iff(inputs.item());
	tr_io io_obj(&iff, cout, MAX_LINE_LEN, inputs.item(),
		     fsa_dict.get_syntax());
	fsa_dict.accent_file(io_obj, accents);
      } while (inputs.next());
      return 0;
    }
    else {
      tr_io io_obj(&cin, cout, MAX_LINE_LEN, "", fsa_dict.get_syntax());
      return fsa_dict.accent_file(io_obj, accents);
    }
  }
  else
    return fsa_dict;
}//main


/* Name:	make_accents_table
 * Class:	None.
 * Purpose:	Read file with accents and prepare accent table.
 * Parameters:	a_file		- (i) name of file with accent descriptions.
 * Returns:	Accent table.
 * Remarks:	The format of the accent file is as follows:
 *			The first character in the first line is a comment
 *			character. Each line that begins with that character
 *			is a comment.
 *			Note: it is usually `#' or ';'.
 *
 *			The first character of non-comment lines is a character
 *			without diacritics. Then, after one or more spaces,
 *			follow characters with diacritics. There are no spaces
 *			between them; they (spaces) indicate the end
 *			of definition.
 *			Characters are represented by themselves, the file
 *			is binary. HT can be defined as accented character.
 *		The format of the accent table:
 *			The table contains 256 characters of codes 0-255.
 *
 *			If a character contains a diacritic, it is represented
 *			by the equivalent latin character.
 *
 *			All other characters are represented by themselves.
 */
accent_tabs *
make_accents_table(const char *file_name)
{
  int		i;
  char		comment_char;
  char		junk;
  unsigned char	buffer[Buf_len];
  char		accented;

  ifstream acc_f(file_name, ios::in /*| ios::nocreate */);
  if (acc_f.bad()) {
    cerr << "Cannot open accent file `" << file_name << "'\n";
    return NULL;
  }
  char *acc_tab = new char[256];
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
  char **cheq = new char *[256];
#endif
  for (i = 0; i < 256; i++) {
    acc_tab[i] = i;
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
    cheq[i] = NULL;
#endif
  }
  if (acc_f.get((char *)buffer, Buf_len, '\n'))
    comment_char = buffer[0];
  else {
    delete [] acc_tab;
    acc_tab = NULL;
    return NULL;
  }
  acc_f.get(junk);
  while (acc_f.get((char *)buffer, Buf_len, '\n')) {
    acc_f.get(junk);
    if ((accented = buffer[0]) != comment_char) {
      for (i = 1; buffer[i] == ' '; i++)
	;
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
      int lb = strlen((char *)buffer);
      unsigned char xc = (unsigned char)accented;
      cheq[xc] = new char[lb + 2];
      strcpy(cheq[xc] + 1, (char *)buffer);
      cheq[xc][0] = xc;
#endif
      for (; buffer[i] != '\0' && buffer[i] != ' '; i++) {
	acc_tab[buffer[i]] = accented;
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
	cheq[buffer[i]] = cheq[xc];
#endif
      }
    }
  }
  accent_tabs *acc_struct = new accent_tabs;
  acc_struct->accents = acc_tab;
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
  acc_struct->eqchs = cheq;
#else
  acc_struct->eqchs = NULL;
#endif
  return acc_struct;
}//make_accents_table
      

/* Name:	usage
 * Class:	None.
 * Purpose:	Prints program synopsis.
 * Parameters:	prog_name	- (i) program name.
 * Returns:	1.
 * Remarks:	None.
 */
int
usage(const char *prog_name)
{
  cerr << "Usage:\n" << prog_name << " [options]...\n"
       << "Options:\n"
       << "-d dictionary\t- automaton file (multiple files allowed)\n"
       << "-a accent_file\t- file with relations between characters\n"
       << "-i input file name (multiple files allowed)\n"
       << "\t[default: standard input]\n"
       << "-l language_file\t- file that defines characters allowed in words\n"
       << "\tand case conversions\n"
       << "\t[default: ASCII letters, standard conversions]\n"
       << "-v version details\n"
       << "Standard output is used for displaying results.\n"
       << "At least one dictionary must be present.\n";
  return 1;
}//usage

/***	EOF accent_main.cc	***/
