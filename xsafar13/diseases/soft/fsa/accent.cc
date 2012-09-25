/***	accent.cc	***/

/*	Copyright (C) Jan Daciuk, 1996-2004	*/


#include        <iostream>
#include	<string.h>
#include        "nstr.h"
#include        "fsa.h"
#include        "common.h"
#include        "accent.h"
      

/* Name:        accent_fsa
 * Class:       accent_fsa
 * Purpose:     Constructor.
 * Parameters:  dict_list       - (i) list of dictionary (fsa) names;
 *		language_file	- (i) file with character set.
 * Returns:     Nothing (constructor).
 * Remarks:     Only to launch fsa contructor.
 */
accent_fsa::accent_fsa(word_list *dict_list, const char *language_file = NULL)
: fsa(dict_list, language_file)
{
}//accent_fsa::accent_fsa
 


/* Name:	accent_file
 * Class:	accent_fsa
 * Purpose:	Restore accents in all words of a file.
 * Parameters:	io_obj		- (i/o) where to read words,
 *					and where to print them;
 *		equiv		- (i) character equivalent classes.
 * Returns:	Exit code.
 * Remarks:	Class variable `replacements' is set to the list of words
 *		equivalent to the `word'.
 */
int
accent_fsa::accent_file(tr_io &io_obj, const accent_tabs *equiv)
{
  int		allocated;
  char		*word;

  word = new char[allocated = Max_word_len];
  while (get_word(io_obj, word, allocated, Max_word_len)) {
    if (accent_word(word, equiv)) {
      io_obj.print_repls(&replacements);
      replacements.empty_list();
    }
    else
      io_obj.print_not_found();
  }
  delete [] word;
  return state;
}//accent_fsa::accent_file




/* Name:	accent_word
 * Class:	accent_fsa
 * Purpose:	Restore accents of a word using all specified dictionaries.
 * Parameters:	word	- (i) word to be checked;
 *		equiv		- (i/o) classes of equivalences for characters.
 * Returns:	Number of words in the list of equivalent words
 *		(stored in replacements).
 * Remarks:	Class variable `replacements' is set to the list of equivalent
 *		words.
 *		The table of equivalent characters contains 256 characters,
 *		and contains:
 *		for characters with diacritics:
 *			- corresponding character without diacritic;
 *		for characters without diacritics:
 *			- that character.
 *		Note: this can be used for other forms of equivalencies,
 *		not necessarily with diacritics.
 */
int
accent_fsa::accent_word(const char *word, const accent_tabs *equiv)
{
  dict_list		*dict;
  fsa_arc_ptr		*dummy = NULL;
#ifdef CASECONV
  int			converted = FALSE;
#endif

  char_eq = equiv->accents;
  same_class = equiv->eqchs;
  dictionary.reset();
  for (dict = &dictionary; dict->item(); dict->next()) {
    set_dictionary(dict->item());
#ifdef CASECONV
    converted = FALSE;
    if (word_syntax[(unsigned char)*word] == 2) {
      // word is uppercase - convert to lowercase
      *((char *)word) = casetab[(unsigned char)*word];
      converted = *word;
    }
#endif
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
    sparse_word_accents(word, 0, sparse_vect->get_first());
#else
    fsa_arc_ptr nxt_node = dummy->first_node(current_dict);
    word_accents(word, 0, nxt_node.set_next_node(current_dict));
#endif
#ifdef CASECONV
    if (converted) {
      // convert back to uppercase
      *((char *)word) = casetab[(unsigned char)*word];
      fsa_arc_ptr xnt_node = dummy->first_node(current_dict);
      word_accents(word, 0, xnt_node.set_next_node(current_dict));
    }
#endif
  }

#ifdef CASECONV
  if (converted) {
    // word was uppercase
    replacements.reset();
    for (;replacements.item();replacements.next()) {
      if (word_syntax[(unsigned char)(replacements.item()[0])] == 3)
	// replacement is lowercase - convert to uppercase
	replacements.item()[0] =
	  casetab[(unsigned char)(replacements.item()[0])];
    }
  }
#endif

  return replacements.how_many();
}//accent_fsa::accent_word


#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
/* Name:	sparse_word_accents
 * Class:	accent_fsa
 * Purpose:	Find all words that have the same letters, but sometimes
 *		with diacritics.
 * Parameters:	word	- (i) word to look for;
 *		level	- (i) how many characters of the word have been
 *				considered so far;
 *		start	- (i) look at that node.
 * Returns:	Number of words on the list of words equivalent to the `word'.
 * Remarks:	Class variable `replacements' is set to the list of words
 *		equivalent to the `word'.
 *		The table of equivalent characters contains 256 characters,
 *		and contains:
 *		for characters with diacritics:
 *			- corresponding character without diacritic;
 *		for characters without diacritics:
 *			- that character.
 *		Note: this can be used for other forms of equivalencies,
 *		not necessarily with diacritics.
 */
int
accent_fsa::sparse_word_accents(const char *word, const int level,
				const long start)
{
  unsigned char	char_no;
  long current = start;
  long next;
  fsa_arc_ptr *dummy;

  if (level + 1 >= cand_alloc)
    grow_string(candidate, cand_alloc, Max_word_len);
  char_no = (unsigned char)(*word);
  if (same_class[char_no]) {
    char *cc = same_class[char_no];
    int l = strlen(cc);
    for (int i = 0; i < l; i++) {
      if ((next = sparse_vect->get_target(current, *cc))
	  != -1L) {
	candidate[level] = *cc;
	if (word[1] == '\0' && sparse_vect->is_final(current, *cc)) {
	  candidate[level + 1] = '\0';
	  replacements.insert_sorted(candidate);
	}
	else {
	  sparse_word_accents(word + 1, level + 1, next);
	}
      }
      cc++;
    }
  }
  else if ((next = sparse_vect->get_target(current, *word)) != -1L) {
    candidate[level] = *word;
    if (word[1] == '\0' && sparse_vect->is_final(current, *word)) {
      candidate[level + 1] = '\0';
      replacements.insert_sorted(candidate);
    }
    else if (*word != ANNOT_SEPARATOR) {
      sparse_word_accents(word + 1, level + 1, next);
    }
    else {
      word_accents(word + 1, level + 1, current_dict + next
#ifdef NUMBERS
		   + dummy->entryl
#endif
		   );
    }
  }
  return replacements.how_many();
}//accent_fsa::sparse_word_accents
#endif //FLEXIBLE&STOPBIT&SPARSE

/* Name:	word_accents
 * Class:	accent_fsa
 * Purpose:	Find all words that have the same letters, but sometimes
 *		with diacritics.
 * Parameters:	word	- (i) word to look for;
 *		level	- (i) how many characters of the word have been
 *				considered so far;
 *		start	- (i) look at that node.
 * Returns:	Number of words on the list of words equivalent to the `word'.
 * Remarks:	Class variable `replacements' is set to the list of words
 *		equivalent to the `word'.
 *		The table of equivalent characters contains 256 characters,
 *		and contains:
 *		for characters with diacritics:
 *			- corresponding character without diacritic;
 *		for characters without diacritics:
 *			- that character.
 *		Note: this can be used for other forms of equivalencies,
 *		not necessarily with diacritics.
 */
int
accent_fsa::word_accents(const char *word, const int level, fsa_arc_ptr start)
{
  fsa_arc_ptr next_node = start;
  unsigned char	char_no;

  if (level + 1 >= cand_alloc)
    grow_string(candidate, cand_alloc, Max_word_len);
  forallnodes(i) {
    char_no = (unsigned char)(next_node.get_letter());
    if (*word == char_eq[char_no]) {
      candidate[level] = next_node.get_letter();
      if (word[1] == '\0' && next_node.is_final()) {
	candidate[level + 1] = '\0';
	replacements.insert_sorted(candidate);
      }
      else {
	fsa_arc_ptr nxt_node = next_node.set_next_node(current_dict);
	word_accents(word + 1, level + 1, nxt_node);
      }
    }
  }
  return replacements.how_many();
}//accent_fsa::word_accents



/***	EOF accent.cc	***/
