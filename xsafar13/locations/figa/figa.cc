#include <ctype.h>

#include "figa.h"

using namespace std;

// trieda data_proc

// nazov: convert_toint
// trieda: data_proc
// popis: konverzia zo stringu na int
int data_proc::convert_toint(string str) {
	int base = 1, digit = 0, i, length, result = 0;

	length = str.length();
	for (i = length - 1; i > -1; i--) {
		if (i != length - 1)
			base *= 10;
		digit = str[i] - '0';
		result += base * digit;
	}
	return result;
} // koniec data_proc::convert_toint

// nazov: process_line
// trieda: data_proc
// popis: spracuje riadok v zozname
Titem data_proc::process_line(string line) {
    Titem tmp;
    int tab, prev;
    
    tab = line.find_first_of('\t');
	tmp.name.assign(line,0,tab);
    
    return tmp;
} // koniec data_proc::process_line

// nazov: get_data
// trieda: data_proc
// popis: najdenym prvkom priradi data z datasetu
void data_proc::get_data(Tmatch match) {
    string line, address;
    int map_line_length;
    // otvaranie suborov
    if (!list_file.is_open() || !map_file.is_open()) {
        cout << "Doslo k chybe pri nacitani datasetu" << endl;
        return;
    }
    getline(map_file, line);
    map_line_length = line.length() + 1;
    
    // priradenie najdenych informacii
    // hash_num je vzdy o jednotku vacsie ako skutocny hash, neviem preco:)
    map_file.seekg((match.hash_num - 1)*map_line_length);
    getline(map_file,address);
	list_file.seekg(atoi(address.c_str()));
	getline(list_file,line);
	match.entry = process_line(line);
	// kontrola najdenych vyrazov, pretoze obcas naslo aj hluposti, ktore vobec nesedeli	
	if (match.entry.name.length() == (match.last_index - match.first_index + 1)/*sem by este kvoli indexacii konca riadkov patrilo aj1.@*/ || match.entry.name.length() == (match.last_index - match.first_index)) {
			cout << match.hash_num << '\t' << match.first_index << '\t' << match.last_index;
			cout << '\t' << line << endl;
	}
}// koniec data_proc::get_data

// trieda marker

// nazov: set_index
// trieda: marker
// popis: nastavi index udavajuci poziciu v texte na nulu
void marker::set_index() {
    index = 0;
    first = 0;
    line_index = 0;
} // koniec marker::set_index

// nazov: next_char
// trieda: marker
// popis: nacita dalsi znak zo vstupu
void marker::next_char() {
    // na konci riadka nacitam dalsi
    if (line.empty() || line_index == line.length()) {
		line_index = 0;
		if (index != 0) // zaratanie konca riadku
			index ++;
		getline(cin, line);
	}
	// nacitanie znaku
	if (!cin.eof()) {
    	a = line[line_index];
    	line_index ++;
    	index ++;
    }
} // koniec marker::next_char

// nazov: next_word
// trieda: marker
// popis: preskoci na zaciatok nasledujuceho vyrazu v texte
void marker::next_word() {
    while ((ispunct(a) || iscntrl(a) || isspace(a)) && !cin.eof()) {
        next_char();
    }
    first = index ;
} // koniec marker::next_word

// nazov: end_word
// trieda: marker
// popis: skoci na koniec slova v texte
void marker::end_word() {
    while ((!ispunct(a) && !isspace(a) && !iscntrl(a)) && !cin.eof()) {
        next_char();
    }
} // koniec marker::end_word

// nazov: save_match
// trieda: marker
// popis: ulozi najdeny vyraz do premennej typu Tmatch
Tmatch marker::save_match(unsigned long int f_index, unsigned long int l_index, int key) {
    Tmatch tmp;
    tmp.first_index = f_index;
    tmp.last_index = l_index;
    tmp.hash_num = key;
    return tmp;
} // koniec marker::save_match

// nazov: match_word
// trieda: marker
// parameter: ukazovatel pre fsa, zvacsa na zaciatok fsa
// popis: prechadza znak po znaku automatom a hlada zhodu
bool marker::match_word(fsa_arc_ptr start) {
    bool found;
    bool fin = false;
    int hash_key = 0;
		
    do {
        fsa_arc_ptr next_node = start.set_next_node(current_dict);
        found = false;
        forallnodes(i) {
            if (a == next_node.get_letter()) {
                found = true;
                start = next_node;
                hash_key += next_node.is_final();
                break;
            }
            else {
                if (next_node.is_final())
                    hash_key ++;
                hash_key += words_in_node(next_node);
            }
        }
        if (!found && fin) {
            dataset.get_data(potencial_match);
            index = potencial_match.last_index; 
            return true;
        } else if (!found) {
            end_word();
            return false;
        }
        next_char();
        if (next_node.is_final() && (ispunct(a) || isspace(a) || iscntrl(a) || cin.eof())) {
            potencial_match = save_match(first, (index -1), hash_key);
            fin = true;
        }
	// ked uz nie je kam ist v automate
        if (next_node.get_goto() == 0) {
			if (fin) {
				dataset.get_data(potencial_match);
				end_word();
				return true;
			}
			end_word();
			return false;
		}
if(fin && cin.eof())
dataset.get_data(potencial_match);
    } while (!cin.eof() && found);
} // koniec marker::match_word



// nazov: lookup
// trieda: marker
// popis: vyhladavanie vo vstupnom texte
int marker::lookup(const char *list_name, const char *map_name) {
    dict_list *my_dict;
    fsa_arc_ptr *dummy = NULL;

    my_dict = &dictionary;
    ANNOT_SEPARATOR = my_dict->item()->annot_sep;
    set_dictionary(my_dict->item());
    
    dataset.list_file.open(list_name);
    dataset.map_file.open(map_name);
    
    set_index();
    next_char();
    while(!cin.eof()) {
        next_word();
        match_word(dummy->first_node(current_dict));
    }

	dataset.list_file.close();
	dataset.map_file.close();
    return 1;
} // koniec marker::lookup
