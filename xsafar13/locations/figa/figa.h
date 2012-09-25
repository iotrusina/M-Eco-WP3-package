// subor: figa.h v0.35
// autor: Marek Visnovsky, xvisno00@stud.fit.vutbr.cz
// popis: kniznica pre znacenie geografickych nazvov v texte

#ifndef FIGA_H
#define FIGA_H

#include <iostream>
#include <string>
#include <fstream>
#include <cstdlib>

#include "fsa.h"
#include "common.h"
#include "nstr.h"

using namespace std;

// struktura pre polozky zoznamu geografickych nazvov
typedef struct {
    string name, geonames_id, freebase_id, type;
} Titem;

// pomocna struktura pre vyhladavanie v zozname
typedef struct {
    int number, hash_num;
} Ttmp_sort;

// struktura pre najdene vyrazy
typedef struct {
    int hash_num;                   /* cislo vyrazu */
    unsigned long int first_index, last_index;  /* pozicia vyrazu */
    Titem entry;
} Tmatch;

// nazov: dataset
// popis: praca so zoznamom
class data_proc {
protected:    	
    int convert_toint(string str);  /* prevod stringu na integer */
    Titem process_line(string line);           /* spracuje riadok v zozname */
    
public:
	ifstream list_file;
	ifstream map_file;
    void get_data(Tmatch match);       /* vytiahne prislusne data zo zoznamu */
};
// nazov: marker
// popis: znaci zhody medzi vyrazmi z fsa a zo vstupu
class marker : public fsa {
protected:
    char a;                         /* znak na vstupe */
    unsigned long int index;        /* aktualna pozicia */
    unsigned int line_index;		/* pozicia na riadku */
    string line;					/* riadok na vstupe */
    unsigned long int first;        /* pozicia prveho znaku najdeneho vyrazu */
    unsigned long int last;         /* posledny znak najdeneho vyrazu */
    Tmatch potencial_match;         /* pomocna premenna pri viacslovnych vyrazoch */
    
    void set_index();               /* vynuluje index */
    void next_char();               /* nacita nasledujuci znak */
    void next_word();               /* preskoci na dalsi vyraz na vstupe */
    void end_word();                /* skoci na koniec slova na vstupe */
    Tmatch save_match(unsigned long int f_index, unsigned long int l_index, int key); /* ulozi najdeny vyraz */
    bool match_word(fsa_arc_ptr start);              /* prechod automatom */
    
public:
    data_proc dataset;              /* praca so zoznamom */
    marker(word_list *dict_names, const char *language_file = NULL) : fsa(dict_names, language_file) {};
    int lookup(const char *list_name, const char *map_name);                   /* vyhladavanie zo standardneho vstupu */
};

#endif
