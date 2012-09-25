/***	common.cc	***/

/* Copyright (C) Jan Daciuk, 1996-2004 */


#include	<iostream>
#include	<fstream>
#include	<string>
#include	<stdlib.h>
#include	<new>
#include	<ctype.h>
#include	"fsa.h"
#include	"nstr.h"
#include	"common.h"

int fsa_arc_ptr::gtl = 2;	// initialization: this must be defined somewhere
int fsa_arc_ptr::size = 4;	// the same
int fsa_arc_ptr::entryl = 0; // the same
int fsa_arc_ptr::aunit = 0; // the same

using namespace std;

/* Name:	fsa
 * Class:	fsa (constructor).
 * Purpose:	Open dictionary files and read automata from them.
 * Parameters:	dict_names	- (i) dictionary file names;
 * Returns:	Nothing.
 * Remarks:	At least one dictionary file must be read.
 */
fsa::fsa(word_list *dict_names, const char *language_file)
{
  int	at_least_one_good = FALSE;

  candidate = new char[cand_alloc = Max_word_len];
  dict_names->reset();
  for (word_list *p = dict_names; p->item() != NULL; p->next())
    at_least_one_good |= read_fsa(p->item());
  state = !at_least_one_good;
  if (language_file)
    read_language_file(language_file);
  else
    invent_language();
}//fsa::fsa

/* Name:	invent_language
 * Class:	fsa
 * Purpose:	Create word_syntax and case tables.
 * Parameters:	None.
 * Returns:	Nothing.
 * Remarks:	Called when no language file is specified.
 *		In the word_syntax table, 3 means lowercase, 2 - uppercase.
 */
void
fsa::invent_language(void)
{
  const char *letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  word_syntax = new char[256];
  for (int i = 0; i < 256; i++)
    word_syntax[i] = 0;
  for (const char *p = letters; *p; p++) {
    if (islower(*p)) {
      word_syntax[(unsigned char)*p] = 3;
      casetab[(unsigned char)*p] = toupper(*p);
    }
    else {
      word_syntax[(unsigned char)*p] = 2;
      casetab[(unsigned char)*p] = tolower(*p);
    }
  }
}//fsa::invent_language


/* Name:	read_language_file
 * Class:	tr_io.
 * Purpose:	Read file with word characters and prepare case table.
 * Parameters:	a_file		- (i) name of file with language description.
 * Returns:	TRUE if succeeded, FALSE otherwise.
 * Remarks:	Two class variables: word_syntax and casetable are set.
 *
 *		The format of the language file is as follows:
 *			The first character in the first line is a comment
 *			character. Each line that begins with that character
 *			is a comment.
 *			Note: it is usually `#' or ';'.
 *
 *			Characters are represented by themselves, the file
 *			is binary.
 *
 *			The first non-comment line contains all characters
 *			that can be used within a word. They normally include
 *			all letters, and may include other characters, such
 *			as a dash, or an apostrophe.
 *
 *		The format of the case table:
 *			The table contains 256 characters of codes 0-255.
 *
 *			For a lowercase letter, the table contains
 *			its uppercase equivalent.
 *			For an uppercase letter, the table contains
 *			its lowercase equivalent.
 *
 *			The other characters are not defined.
 *
 *		In the word_syntax table, 3 means lowercase, 2 - uppercase.
 */
int
fsa::read_language_file(const char *file_name)
{
  const int	Buf_len = 512;
  int		i;
  char		comment_char;
  char		junk;
  unsigned char	buffer[Buf_len];
  unsigned char	first;

  ifstream lang_f(file_name, ios::in /*| ios::nocreate */);
  if (lang_f.bad()) {
    cerr << "Cannot open language file `" << file_name << "'\n";
    return FALSE;
  }
  char *word_tab = new char[256];
  for (i = 0; i < 256; i++)
    word_tab[i] = '\0';
  if (lang_f.get((char *)buffer, Buf_len, '\n'))
    comment_char = buffer[0];
  else
    return FALSE;
  lang_f.get(junk);
  if (junk != '\n')
    cerr << "Lines in language file " << file_name << " are too long!\n";
  int read_word_chars = TRUE;
  while (read_word_chars && lang_f.get((char *)buffer, Buf_len, '\n')) {
    lang_f.get(junk);
    if (junk != '\n')
      cerr << "Lines in language file " << file_name << " are too long!\n";
    if ((first = buffer[0]) != comment_char) {
      for (unsigned char *p = buffer; *p; p++) {
	word_tab[*p] = TRUE;
      }
      read_word_chars = FALSE;
    }
  }//while
  int read_case = TRUE;
  // first is lowercase
  int upper = 3;	// in word_tab, uppercase is marked with 2, lowercase 3
  while (read_case && lang_f.get((char *)buffer, Buf_len, '\n')) {
    lang_f.get(junk);
    if (junk != '\n')
      cerr << "Lines in language file " << file_name << " are too long!\n";
    if ((first = buffer[0]) != comment_char) {
      for (unsigned char *p = buffer; *p; p++) {
	word_tab[*p] = upper;
	if (upper == 2) {
	  // second letter in pair, first is in `first'
	  casetab[first] = (char)*p;
	  casetab[*p] = (char)first;
	}
	upper = 5 - upper;		// flip case
	first = *p;
      }
      read_word_chars = FALSE;
    }
  }//while
  word_syntax = word_tab;
  return TRUE;
}//fsa::read_language_file

/* Name:	read_fsa
 * Class:	fsa
 * Purpose:	Reads an automaton from a specified file and places it
 *		on a list of dictionaries.
 * Parameters:	dict_file_name	- (i) dictionary file name.
 * Returns:	TRUE if success, FALSE if failed.
 * Remarks:	None.
 */
int
fsa::read_fsa(const char *dict_file_name)
{
  const int	version = 5;	// FLEXIBLE,STOPBIT,NEXTBIT,!TAILS,!WEIGHTED
  streampos	file_ptr;
  long int	file_size;
  int		no_of_arcs;
  fsa_arc_ptr	new_fsa;
  signature	sig_arc;	/* magic number at the beginning of fsa */
  dict_desc	dd;
  int		arc_size;

  // open dictionary file
  ifstream dict(dict_file_name, ios::in /*| ios::nocreate*/ | ios::ate |
		ios::binary);	// this one is for M$'s bugs
  if (dict.bad()) {
    cerr << "Cannot open dictionary file " << dict_file_name << "\n";
    return(FALSE);
  }

  // see how many arcs are there
  // There is a bug in libstdc++ distributed in rpms.
  // This is a workaround (thanks to Arnaud Adant <arnaud.adant@supelec.fr>
  // for pointing this out).
  if (!dict.seekg(0,ios::end)) {
    cerr << "Seek on dictionary file failed. File is "
         << dict_file_name << "\n";
    return FALSE;
  }
  file_ptr = dict.tellg();
  file_size = file_ptr;
  if (!dict.seekg(0L)) {
    cerr << "Seek on dictionary file failed. File is "
         << dict_file_name << "\n";
    return FALSE;
  }

  // read and verify signature
  if (!(dict.read((char *)&sig_arc, sizeof(sig_arc)))) {
    cerr << "Cannot read dictionary file " << dict_file_name << "\n";
    return(FALSE);
  }
  if (strncmp(sig_arc.sig, "\\fsa", (size_t)4)) {
    cerr << "Invalid dictionary file (bad magic number): " << dict_file_name
      << endl;
    return(FALSE);
  }
  if (sig_arc.ver != version && !(sig_arc.ver == 5 && version == 8)) {
    cerr << "Invalid dictionary version in file: " << dict_file_name << endl
	 << "Version number is " << int(sig_arc.ver)
	 << " which indicates dictionary was build:" << endl;
    switch (sig_arc.ver) {
    case 0:
      cerr << "without FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "without STOPBIT, without NEXTBIT" << endl;
      break;
    case '\x80':
      cerr << "without FLEXIBLE, with LARGE DICTIONARIES, "
	   << "without STOPBIT, without NEXTBIT" << endl;
      break;
    case 1:
      cerr << "with FLEXIBLE, without LARGE DICTIONARIES, "
	   << "without STOPBIT, without NEXTBIT" << endl;
      break;
    case 2:
      cerr << "with FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "without STOPBIT, with NEXTBIT" << endl;
      break;
    case 4:
      cerr << "with FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "with STOPBIT, without NEXTBIT, without TAILS" << endl;
      break;
    case 5:
      cerr << "with FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "with STOPBIT, with NEXTBIT, without TAILS" << endl;
      break;
    case 6:
      cerr << "with FLEXIBLE,  without LARGE_DICTIONARIES, "
	   << "with STOPBIT, without NEXTBIT, with TAILS" << endl;
      break;
    case 7:
      cerr << "with FLEXIBLE,  without LARGE_DICTIONARIES, "
	   << "with STOPBIT, with NEXTBIT, with TAILS" << endl;
      break;
    case 9:
      cerr << "with FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "with STOPBIT, without NEXTBIT, without TAILS, with SPARSE"
	   << endl;
    case 10:
       cerr << "with FLEXIBLE, without LARGE_DICTIONARIES, "
	   << "with STOPBIT, with NEXTBIT, without TAILS, with SPARSE" << endl;
      break;
    case 11:
      cerr << "with FLEXIBLE,  without LARGE_DICTIONARIES, "
	   << "with STOPBIT, without NEXTBIT, with TAILS, with SPARSE" << endl;
      break;
    case 12:
      cerr << "with FLEXIBLE,  without LARGE_DICTIONARIES, "
	   << "with STOPBIT, with NEXTBIT, with TAILS, with SPARSE" << endl;
      break;
    default:
      cerr << "with yet unknown compile options (upgrade your software)"
	   << endl;
    }
    return FALSE;
  }

  FILLER = sig_arc.filler;
  ANNOT_SEPARATOR = sig_arc.annot_sep;
  new_fsa.gtl = sig_arc.gtl & 0x0f;
  new_fsa.size = new_fsa.gtl + goto_offset;
  new_fsa.entryl = (sig_arc.gtl >> 4) & 0x0f;
  new_fsa.aunit = (new_fsa.entryl ? 1 : new_fsa.size);

  // allocate memory and read the automaton
  arc_size = 1;
  no_of_arcs = (long)file_size - sizeof(sig_arc);
  new_fsa = new char[no_of_arcs];
//#ifdef NUMBERS
//  if (new_fsa.entryl) {
//    no_of_arcs = (long)file_size - sizeof(sig_arc);
//    new_fsa = new char[no_of_arcs];
//    arc_size = 1; // for use in reading later on to specify how much to read
 // }
//  else {
//#endif //NUMBERS
  arc_size = goto_offset + sig_arc.gtl;
  no_of_arcs = ((long)file_size - sizeof(sig_arc)) / arc_size;
  if ((long)arc_size * no_of_arcs != ((long)file_size - (long)sizeof(sig_arc)))
    no_of_arcs++;
  new_fsa = new char[((long)file_size - sizeof(sig_arc))];
//#ifdef NUMBERS
//  }
//#endif //NUMBERS
  if (!(dict.read((char *)(new_fsa.arc), ((long)file_size-sizeof(sig_arc))))) {
    cerr << "Cannot read dictionary file " << dict_file_name << "\n";
    return(FALSE);
  }

  // put the automaton on the list of dictionaries
  dd.filler = FILLER;
  dd.annot_sep = ANNOT_SEPARATOR;
  dd.gtl = new_fsa.gtl;
  dd.entryl = new_fsa.entryl;
  dd.dict = new_fsa;
  dd.no_of_arcs = no_of_arcs;
  dictionary.insert(&dd);
  return TRUE;
}//fsa::read_fsa

/* Name:	word_in_dictionary
 * Class:	fsa.
 * Purpose:	Find if a word is in a dictionary (automaton).
 * Parameters:	word	- (i) word to check;
 *		start	- (i) look at children of this node.
 * Returns:	TRUE if word found, FALSE otherwise.
 * Remarks:	None.
 */
int
fsa::word_in_dictionary(const char *word, fsa_arc_ptr start)
{
  bool found = false;
  fsa_arc_ptr next_node = start;
  do {
    found = false;
    forallnodes(i) {
      if (*word == next_node.get_letter()) {
	if (word[1] == '\0' && next_node.is_final())
	  return TRUE;
	else {
	  word++;
	  start = next_node;
	  found = TRUE;
	  break;
	}
      }
    }
    next_node = start.set_next_node(current_dict);
  } while (found);
  return FALSE;
}//fsa::word_in_dictionary

/* Name:	set_dictionary
 * Class:	fsa
 * Purpose:	Sets variables associated with the current dictionary
 * Parameters:	dict	- (i) current dictionary description.
 * Returns:	Nothing.
 * Remarks:	None.
 */
void
fsa::set_dictionary(dict_desc *dict)
{
  fsa_arc_ptr	dummy(NULL);

  current_dict = dict->dict.arc;
  FILLER = dict->filler;
  dummy.gtl = dict->gtl;
  dummy.size = dummy.gtl + goto_offset;
  dummy.entryl = dict->entryl;
  dummy.aunit = dummy.entryl ? 1 : (goto_offset + dummy.gtl);
}//fsa::set_dictionary

/* Name:	word_in_dictionaries
 * Class:	fsa
 * Purpose:	Searches for the word in all dictionaries.
 * Parameters:	word	- (i) word to be checked.
 * Returns:	TRUE if the word is in the dictionaries, FALSE otherwise.
 * Remarks:	I don't know why it was not present here before.
 */
int
fsa::word_in_dictionaries(const char *word)
{
  dict_list		*dict;
  fsa_arc_ptr		*dummy = NULL;

  dictionary.reset();
  for (dict = &dictionary; dict->item(); dict->next()) {
    set_dictionary(dict->item());
    fsa_arc_ptr nxtnode = dummy->first_node(current_dict);
    if (word_in_dictionary(word, nxtnode.set_next_node(current_dict)))
      return TRUE;
    else if (word_syntax[(unsigned char)*word] == 2) {
      // word is uppercase - try lowercase
      *((char *)word) = casetab[(unsigned char)*word];
      fsa_arc_ptr nxtnode = dummy->first_node(current_dict);
      if (word_in_dictionary(word, nxtnode.set_next_node(current_dict)))
	return TRUE;
      *((char *)word) = casetab[(unsigned char)*word];
    }
  }
  return FALSE;
}//fsa::word_in_dictionaries

/* Name:	words_in_node
 * Class:	hash_fsa
 * Purpose:	Returns the number of different words (word suffixes)
 *		in the given node.
 * Parameters:	start		- (i) parent of the node to be examined.
 * Returns:	Number of different word suffixes in the given node.
 * Remarks:	None.
 */
int
fsa::words_in_node(fsa_arc_ptr start)
{
  fsa_arc_ptr next_node = start.set_next_node(current_dict);

  return (start.get_goto() ?
	  bytes2int((unsigned char *)next_node.arc - next_node.entryl,
		    next_node.entryl)
	  : 0);
}//hash_fsa::words_in_node

/* Name:	get_word
 * Class:	None.
 * Purpose:	Read a word from input, allocating more memory if necessary.
 * Parameters:	io_obj		- (i/o) where to read from;
 *		word		- (o) line to be read;
 *		allocated	- (i/o) size of buffer before/after read;
 *		alloc_step	- how much allocated may differ between calls.
 * Returns:	io_obj.
 * Remarks:	This is necessary to prevent buffer overflows.
 *		It is assumed that a word is the same as one line.
 *		An ifdef is needed for text_io input.
 */
tr_io &
get_word(tr_io &io_obj, char *&word, int &allocated,
	 const int alloc_step)
{
  char *w;

  io_obj.set_buf_len(allocated);
  if (io_obj >> word) {
    if (io_obj.get_junk() != '\n') {
      io_obj.set_buf_len(alloc_step);
      do {
	w = grow_string(word, allocated, alloc_step);
	w += allocated - alloc_step;
	word[allocated - alloc_step - 1] = io_obj.get_junk();
	if (!(io_obj >> w)) {
	  break;
	}
      } while (io_obj.get_junk() != '\n');
      io_obj.set_buf_len(allocated);
    }
  }
  return io_obj;
}//get_word

/***	EOF common.cc	***/
