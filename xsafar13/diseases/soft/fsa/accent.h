/***	accent.h		***/

/*	Copyright (c) Jan Daciuk, 1996-2004	*/

struct accent_tabs {
  /* For every character: either itself or a character without diacritics */
  char *accents;
  /* For characters that may have diacritics: all equivalent characters */
  char **eqchs;
};

class accent_fsa : public fsa {
protected:
  const char		*char_eq;
  char			**same_class;
public:
  accent_fsa(word_list *dict_names, const char *language_file);
  virtual ~accent_fsa(void) {}
#if defined(FLEXIBLE) && defined(STOPBIT) && defined(SPARSE)
  int sparse_word_accents(const char *word, const int level,
			  const long start);
#endif
  int word_accents(const char *word, const int level,
			  fsa_arc_ptr start);
  int accent_word(const char *word, const accent_tabs *equiv);
  int accent_file(tr_io &io_obj, const accent_tabs *equiv);
};/*class accent_fsa*/

/***	EOF accent.fsa	***/
