/***	morph_main.cc	***/

/*	Copyright (C) Jan Daciuk, 1996-2004	*/

/*
   This program performs a morphological analysis of words.
   It uses a dictionary in form of an automaton.

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
#include	"morph.h"
#include	"fsa_version.h"

static const int	MAX_LINE_LEN = 512;	// Buffer length for input

int
main(const int argc, const char *argv[]);
int
usage(const char *prog_name);
void
not_enough_memory(void);



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
 * Remarks:	None.
 */
int
main(const int argc, const char *argv[])
{
  word_list	dict;		// dictionary file name 
  int		arg_index;	// current argument number
  word_list	inputs;		// names of input files (if any)
  const char	*lang_file = NULL; // name of file with character set
#ifdef MORPH_INFIX
  int		file_has_infixes = FALSE;
  int		file_has_prefixes = FALSE;
#endif
#ifdef POOR_MORPH
  int		only_categories = FALSE;
#endif
  int		ignore_filler = FALSE;

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
#ifdef MORPH_INFIX
    else if (argv[arg_index][1] == 'I') {
      // dictionary contains coded infixes
      file_has_infixes = TRUE;
    }
    else if (argv[arg_index][1] == 'P') {
      // dictionary contains coded prefixes
      file_has_prefixes = TRUE;
    }
    
#endif
    else if (argv[arg_index][1] == 'F') {
      // dictionary contains coded prefixes
      ignore_filler = TRUE;
    }
#ifdef POOR_MORPH
    else if (argv[arg_index][1] == 'A') {
      // dictionary contains no information on base forms
      only_categories = TRUE;
    }
#endif
    else if (argv[arg_index][1] == 'v') {
      // version details
#include "compile_options.h"
      return 0;
    }
    else {
      cerr << argv[0] << ": unrecognized option\n";
      return usage(argv[0]);
    }
  }//for

  if (dict.how_many() == 0) {
    cerr << argv[0] << ": at least one dictionary file must be specified\n";
    return usage(argv[0]);
  }

#ifdef MORPH_INFIX
#ifdef POOR_MORPH
  morph_fsa fsa_dict(ignore_filler, only_categories, file_has_infixes,
		     file_has_prefixes, &dict, lang_file);
#else
  morph_fsa fsa_dict(ignore_filler, file_has_infixes, file_has_prefixes,
		     &dict, lang_file);
#endif
#else
#ifdef POOR_MORPH
  morph_fsa fsa_dict(ignore_filler, only_categories, &dict, lang_file);
#else
  morph_fsa fsa_dict(ignore_filler, &dict, lang_file);
#endif
#endif
  if (!fsa_dict) {
    if (inputs.how_many()) {
      inputs.reset();
      do {
	ifstream iff(inputs.item());
	tr_io io_obj(&iff, cout, MAX_LINE_LEN, inputs.item(),
		     fsa_dict.get_syntax());
	fsa_dict.morph_file(io_obj);
      } while (inputs.next());
      return 0;
    }
    else {
      tr_io io_obj(&cin, cout, MAX_LINE_LEN, "", fsa_dict.get_syntax());
      return fsa_dict.morph_file(io_obj);
    }
  }
  else
    return fsa_dict;
}//main


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
       << "-i input file name (multiple files allowed)\n"
       << "\t[default: standard input]\n"
       << "-l language_file\t- file that defines characters allowed in words\n"
       << "\tand case conversions\n"
       << "\t[default: ASCII letters, standard conversions]\n"
       << "-F\t- ignore filler character (default: don't ignore)\n"
#ifdef MORPH_INFIX
       << "-I\t- use when dictionary contains coded infixes\n"
       << "-P\t- use when dictionary contains coded prefixes\n"
#endif
#ifdef POOR_MORPH
       << "-A\t- use when dictionary contains no information on base forms\n"
#endif
       << "-v version details\n"
       << "Standard output is used for displaying results.\n"
       << "At least one dictionary must be present.\n";
  return 1;
}//usage

/***	EOF morph_main.cc	***/
